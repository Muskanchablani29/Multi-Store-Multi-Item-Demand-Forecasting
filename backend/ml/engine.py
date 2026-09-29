import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import os

SEQ_LEN = 10
EPOCHS = 50
BATCH_SIZE = 16


def prepare_sequences(series, seq_len=SEQ_LEN):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.reshape(-1, 1))
    X, y = [], []
    for i in range(len(scaled) - seq_len):
        X.append(scaled[i:i + seq_len])
        y.append(scaled[i + seq_len])
    return np.array(X), np.array(y), scaler


def build_model(model_type, seq_len):
    model = Sequential()
    layer = LSTM if model_type == 'LSTM' else GRU
    model.add(layer(64, input_shape=(seq_len, 1), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(layer(32))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model


def train_and_evaluate(sales_qs, shop_id, product_id, model_type, models_dir):
    df = pd.DataFrame(list(sales_qs.values('date', 'quantity'))).sort_values('date')
    if len(df) < SEQ_LEN + 5:
        raise ValueError(f"Not enough data. Need at least {SEQ_LEN + 5} records.")

    series = df['quantity'].values.astype(float)
    split = int(len(series) * 0.8)
    train_series, test_series = series[:split], series[split:]

    X_train, y_train, scaler = prepare_sequences(train_series)
    full_X, full_y, _ = prepare_sequences(series)
    X_test = full_X[split - SEQ_LEN:]
    y_test = full_y[split - SEQ_LEN:]

    model = build_model(model_type, SEQ_LEN)
    model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=0.1,
        callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
        verbose=0
    )

    model_path = os.path.join(models_dir, f"{model_type}_{shop_id}_{product_id}.keras")
    model.save(model_path)

    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred = scaler.inverse_transform(y_pred_scaled).flatten()
    y_actual = scaler.inverse_transform(y_test).flatten()

    mae = float(mean_absolute_error(y_actual, y_pred))
    mse = float(mean_squared_error(y_actual, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_actual, y_pred))

    return {
        'mae': mae, 'mse': mse, 'rmse': rmse, 'r2': r2,
        'actual': y_actual.tolist(),
        'predicted': y_pred.tolist(),
        'dates': df['date'].astype(str).tolist()[split:]
    }


def forecast_future(sales_qs, shop_id, product_id, model_type, steps, models_dir):
    model_path = os.path.join(models_dir, f"{model_type}_{shop_id}_{product_id}.keras")
    if not os.path.exists(model_path):
        raise FileNotFoundError("Model not trained yet. Train the model first.")

    model = load_model(model_path)
    df = pd.DataFrame(list(sales_qs.values('date', 'quantity'))).sort_values('date')
    series = df['quantity'].values.astype(float)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(series.reshape(-1, 1))
    last_seq = scaled[-SEQ_LEN:].reshape(1, SEQ_LEN, 1)

    predictions = []
    for _ in range(steps):
        pred = model.predict(last_seq, verbose=0)[0][0]
        predictions.append(pred)
        last_seq = np.append(last_seq[:, 1:, :], [[[pred]]], axis=1)

    forecast_values = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

    last_date = pd.to_datetime(df['date'].max())
    forecast_dates = [
        (last_date + pd.Timedelta(days=i + 1)).strftime('%Y-%m-%d')
        for i in range(steps)
    ]

    return list(zip(forecast_dates, forecast_values.tolist()))
