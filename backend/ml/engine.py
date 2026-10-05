"""
ml/engine.py
Demand forecasting engine — LSTM / GRU.

Key design decisions
--------------------
1. DAILY AGGREGATION  : raw transaction rows are summed per date before any
                        modelling.  The model learns daily demand, not per-
                        transaction noise.
2. SEQUENCE LENGTH    : 30 days (one month of context).
3. ARCHITECTURE       : two stacked layers (128 → 64) + BatchNorm + Dropout.
4. SCALING            : qty_scaler and feat_scaler are both fitted on the
                        FULL dataset so the test window is never out-of-range.
5. TRAIN/TEST SPLIT   : 80 / 20 on the aggregated daily series.
6. EARLY STOPPING     : patience=10, restore_best_weights=True.
7. REDUCE LR          : ReduceLROnPlateau halves LR when val_loss plateaus.
8. FORECAST           : rolling window with day-of-week / month / season
                        advanced correctly for each future step.
"""

import os
import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

# ── Hyper-parameters ─────────────────────────────────────────────────────────
SEQ_LEN    = 30      # days of history per input window
EPOCHS     = 100
BATCH_SIZE = 32

# ── Encodings ────────────────────────────────────────────────────────────────
SEASON_MAP = {
    'Winter': 0, 'Summer': 1, 'Monsoon': 2,
    'Festival': 3, 'School Season': 4, 'School': 4,
}

FEATURE_COLS = [
    'quantity',           # target (index 0)
    'unit_price',
    'discount_percent',
    'promotion_int',
    'is_holiday_int',
    'day_of_week',
    'month',
    'is_weekend_int',
    'season_enc',
    'day_of_year_sin',    # cyclical encoding of day-of-year
    'day_of_year_cos',
    'month_sin',
    'month_cos',
]


# ── Step 1 : aggregate transactions → daily demand ───────────────────────────

def _aggregate_daily(sales_qs):
    """
    Sum all transaction rows for the same (shop, product, date) into a single
    daily demand record.  Returns a DataFrame sorted by date with one row per
    calendar day that had at least one sale.
    """
    fields = [
        'date', 'quantity', 'unit_price', 'discount_percent',
        'promotion', 'is_holiday', 'day_of_week', 'month',
        'is_weekend', 'season',
    ]
    df = pd.DataFrame(list(sales_qs.values(*fields)))

    if df.empty:
        return df

    # Aggregate numeric fields
    agg = df.groupby('date').agg(
        quantity        = ('quantity',         'sum'),
        unit_price      = ('unit_price',       'mean'),
        discount_percent= ('discount_percent', 'mean'),
        promotion       = ('promotion',        'max'),   # 1 if any txn had promo
        is_holiday      = ('is_holiday',       'max'),
        day_of_week     = ('day_of_week',      'first'),
        month           = ('month',            'first'),
        is_weekend      = ('is_weekend',       'max'),
        season          = ('season',           'first'),
    ).reset_index().sort_values('date').reset_index(drop=True)

    return agg


# ── Step 2 : build feature matrix ────────────────────────────────────────────

def _build_features(df):
    """Convert aggregated daily DataFrame → 2-D numpy array (days × features)."""
    df = df.copy()

    df['promotion_int']  = df['promotion'].astype(int)
    df['is_holiday_int'] = df['is_holiday'].astype(int)
    df['is_weekend_int'] = df['is_weekend'].astype(int)
    df['season_enc']     = df['season'].map(SEASON_MAP).fillna(0).astype(float)

    # Cyclical time features — help the model understand periodicity
    doy = pd.to_datetime(df['date']).dt.dayofyear
    df['day_of_year_sin'] = np.sin(2 * np.pi * doy / 365)
    df['day_of_year_cos'] = np.cos(2 * np.pi * doy / 365)
    df['month_sin']       = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos']       = np.cos(2 * np.pi * df['month'] / 12)

    for col in ['unit_price', 'discount_percent', 'day_of_week', 'month']:
        if col not in df.columns:
            df[col] = 0

    return df[FEATURE_COLS].fillna(0).values.astype(float)


# ── Step 3 : create sequences ────────────────────────────────────────────────

def _make_sequences(scaled, qty_scaled, seq_len):
    X, y = [], []
    for i in range(len(scaled) - seq_len):
        X.append(scaled[i: i + seq_len])
        y.append(qty_scaled[i + seq_len, 0])
    return np.array(X), np.array(y)


# ── Step 4 : build model ─────────────────────────────────────────────────────

def build_model(model_type, seq_len, n_features):
    Layer = LSTM if model_type == 'LSTM' else GRU
    model = Sequential([
        Layer(128, input_shape=(seq_len, n_features), return_sequences=True),
        BatchNormalization(),
        Dropout(0.2),
        Layer(64, return_sequences=False),
        BatchNormalization(),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(1),
    ])
    model.compile(optimizer=Adam(learning_rate=1e-3), loss='huber')
    return model


# ── Public API ────────────────────────────────────────────────────────────────

def train_and_evaluate(sales_qs, shop_id, product_id, model_type, models_dir):
    # 1. Aggregate to daily demand
    df = _aggregate_daily(sales_qs)
    if df.empty or len(df) < SEQ_LEN + 10:
        raise ValueError(
            f"Not enough daily data. Need at least {SEQ_LEN + 10} days with sales "
            f"(got {len(df)}). Upload more data first."
        )

    # 2. Build feature matrix
    data = _build_features(df)          # shape: (days, n_features)
    n_features = data.shape[1]

    # 3. Scale — fit on FULL dataset to avoid out-of-range test values
    qty_scaler  = MinMaxScaler(feature_range=(0, 1))
    feat_scaler = MinMaxScaler(feature_range=(0, 1))

    qty_scaled  = qty_scaler.fit_transform(data[:, 0:1])
    feat_scaled = feat_scaler.fit_transform(data[:, 1:])
    scaled      = np.hstack([qty_scaled, feat_scaled])

    # 4. Train / test split (80 / 20) on the daily series
    split = int(len(scaled) * 0.8)
    if split <= SEQ_LEN:
        raise ValueError("Training set too small after 80/20 split.")

    X_train, y_train = _make_sequences(scaled[:split],  qty_scaled[:split],  SEQ_LEN)
    X_test,  y_test  = _make_sequences(scaled[split - SEQ_LEN:],
                                        qty_scaled[split - SEQ_LEN:], SEQ_LEN)

    # 5. Train
    model = build_model(model_type, SEQ_LEN, n_features)
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10,
                      restore_best_weights=True, verbose=0),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                          patience=5, min_lr=1e-6, verbose=0),
    ]
    model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=0,
    )

    # 6. Save model + scalers
    os.makedirs(models_dir, exist_ok=True)
    model_path   = os.path.join(models_dir, f"{model_type}_{shop_id}_{product_id}.keras")
    scalers_path = model_path.replace('.keras', '_scalers.pkl')
    model.save(model_path)
    with open(scalers_path, 'wb') as f:
        pickle.dump({'qty': qty_scaler, 'feat': feat_scaler}, f)

    # 7. Evaluate on test set
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred  = qty_scaler.inverse_transform(y_pred_scaled).flatten()
    y_actual = qty_scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    mae  = float(mean_absolute_error(y_actual, y_pred))
    mse  = float(mean_squared_error(y_actual, y_pred))
    rmse = float(np.sqrt(mse))
    r2   = float(r2_score(y_actual, y_pred))

    # 8. Return test-window dates (daily, not transaction-level)
    test_dates = df['date'].astype(str).tolist()[split:]

    return {
        'mae': mae, 'mse': mse, 'rmse': rmse, 'r2': r2,
        'actual':    y_actual.tolist(),
        'predicted': y_pred.tolist(),
        'dates':     test_dates,
        'train_days': split,
        'test_days':  len(y_actual),
        'total_days': len(df),
    }


def forecast_future(sales_qs, shop_id, product_id, model_type, steps, models_dir):
    model_path   = os.path.join(models_dir, f"{model_type}_{shop_id}_{product_id}.keras")
    scalers_path = model_path.replace('.keras', '_scalers.pkl')

    if not os.path.exists(model_path):
        raise FileNotFoundError("Model not trained yet. Train the model first.")

    # Load scalers
    if os.path.exists(scalers_path):
        with open(scalers_path, 'rb') as f:
            scalers = pickle.load(f)
        qty_scaler  = scalers['qty']
        feat_scaler = scalers['feat']
    else:
        # Fallback: refit on current data
        df_tmp  = _aggregate_daily(sales_qs)
        data_tmp = _build_features(df_tmp)
        qty_scaler  = MinMaxScaler().fit(data_tmp[:, 0:1])
        feat_scaler = MinMaxScaler().fit(data_tmp[:, 1:])

    model = load_model(model_path)

    # Build the seed window from the last SEQ_LEN daily records
    df   = _aggregate_daily(sales_qs)
    data = _build_features(df)

    qty_scaled  = qty_scaler.transform(data[:, 0:1])
    feat_scaled = feat_scaler.transform(data[:, 1:])
    scaled      = np.hstack([qty_scaled, feat_scaled])

    last_seq = scaled[-SEQ_LEN:].copy()   # (SEQ_LEN, n_features)
    last_date = pd.to_datetime(df['date'].max())

    predictions  = []
    forecast_dates = []

    for step in range(steps):
        next_date = last_date + pd.Timedelta(days=step + 1)

        # Predict
        x_input = last_seq.reshape(1, SEQ_LEN, data.shape[1])
        pred_scaled = model.predict(x_input, verbose=0)[0][0]
        predictions.append(pred_scaled)

        # Build next feature row with correct calendar values
        dow     = next_date.dayofweek
        month   = next_date.month
        is_wknd = 1 if dow >= 5 else 0
        doy     = next_date.dayofyear
        # Keep unit_price, discount, promotion, holiday, season from last known row
        last_feat_raw = feat_scaler.inverse_transform(last_seq[-1:, 1:])[0]
        # Overwrite time features (indices in feat cols after qty):
        # feat order: unit_price(0), discount_percent(1), promotion_int(2),
        #             is_holiday_int(3), day_of_week(4), month(5),
        #             is_weekend_int(6), season_enc(7),
        #             day_of_year_sin(8), day_of_year_cos(9),
        #             month_sin(10), month_cos(11)
        last_feat_raw[4]  = dow
        last_feat_raw[5]  = month
        last_feat_raw[6]  = is_wknd
        last_feat_raw[8]  = np.sin(2 * np.pi * doy / 365)
        last_feat_raw[9]  = np.cos(2 * np.pi * doy / 365)
        last_feat_raw[10] = np.sin(2 * np.pi * month / 12)
        last_feat_raw[11] = np.cos(2 * np.pi * month / 12)
        # is_holiday: set 0 for future (unknown)
        last_feat_raw[3]  = 0

        new_feat_scaled = feat_scaler.transform(last_feat_raw.reshape(1, -1))[0]
        new_row = np.concatenate([[pred_scaled], new_feat_scaled])

        # Slide window
        last_seq = np.vstack([last_seq[1:], new_row])
        forecast_dates.append(next_date.strftime('%Y-%m-%d'))

    forecast_values = qty_scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    ).flatten()

    # Clip negatives (demand can't be negative)
    forecast_values = np.clip(forecast_values, 0, None)

    return list(zip(forecast_dates, forecast_values.tolist()))
