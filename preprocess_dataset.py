"""
preprocess_dataset.py
Cleans thakur_footwear_sales_500k.csv and writes
thakur_footwear_cleaned.csv ready for model training.

Steps
-----
1.  Load & basic inspection
2.  Drop exact duplicate rows
3.  Drop duplicate sale_id
4.  Parse & validate date column
5.  Fix mixed-type / missing holiday_name
6.  Validate & fix boolean columns (is_weekend, is_holiday, promotion)
7.  Validate categorical columns (season, promotion_type, gender, category)
8.  Remove rows with non-positive quantity
9.  Remove rows with negative prices
10. Remove rows where cost_price >= unit_price
11. Clip discount_percent to [0, 100]
12. Recompute derived columns (discount_amount, total_sales, profit)
13. Outlier removal on quantity using IQR per product
14. Recompute / validate time features (day_of_week, month, is_weekend)
15. Save cleaned CSV + print summary report
"""

import numpy as np
import pandas as pd

INPUT  = "thakur_footwear_sales_500k.csv"
OUTPUT = "thakur_footwear_cleaned.csv"

SEASON_MAP = {
    1: "Winter", 2: "Winter", 3: "Summer", 4: "Summer",  5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Festival", 11: "Festival", 12: "Winter",
}

VALID_SEASONS    = {"Winter", "Summer", "Monsoon", "Festival", "School Season"}
VALID_GENDERS    = {"Men", "Women", "Kids", "Unisex"}
VALID_CATEGORIES = {
    "Running Shoes", "Casual Shoes", "Formal Shoes", "Sandals",
    "Boots", "Sports Shoes", "School Shoes", "Slippers",
}

# ── 1. Load ───────────────────────────────────────────────────────────────────
print("Loading dataset …")
df = pd.read_csv(INPUT, low_memory=False)
initial_rows = len(df)
print(f"  Loaded : {initial_rows:,} rows × {df.shape[1]} columns")

report = {}   # collects counts of every fix applied

# ── 2. Drop exact duplicate rows ─────────────────────────────────────────────
before = len(df)
df.drop_duplicates(inplace=True)
report["exact_duplicate_rows_dropped"] = before - len(df)
print(f"  Exact duplicates dropped      : {report['exact_duplicate_rows_dropped']:,}")

# ── 3. Drop duplicate sale_id ────────────────────────────────────────────────
before = len(df)
df.drop_duplicates(subset="sale_id", keep="first", inplace=True)
report["duplicate_sale_id_dropped"] = before - len(df)
print(f"  Duplicate sale_id dropped     : {report['duplicate_sale_id_dropped']:,}")

# ── 4. Parse & validate date ─────────────────────────────────────────────────
df["date"] = pd.to_datetime(df["date"], errors="coerce")
before = len(df)
df.dropna(subset=["date"], inplace=True)
report["invalid_date_dropped"] = before - len(df)
print(f"  Invalid date rows dropped     : {report['invalid_date_dropped']:,}")

# ── 5. Fix holiday_name (NaN → empty string) ─────────────────────────────────
null_holiday = df["holiday_name"].isnull().sum()
df["holiday_name"] = df["holiday_name"].fillna("").astype(str).str.strip()
report["holiday_name_nulls_filled"] = int(null_holiday)
print(f"  holiday_name nulls filled     : {report['holiday_name_nulls_filled']:,}")

# ── 6. Validate boolean columns ───────────────────────────────────────────────
for col in ["is_weekend", "is_holiday", "promotion"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int).clip(0, 1)

# Recompute is_weekend & day_of_week from date (source of truth)
df["day_of_week"] = df["date"].dt.dayofweek          # 0=Mon … 6=Sun
df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)
df["month"]       = df["date"].dt.month
df["quarter"]     = df["date"].dt.quarter
report["time_features_recomputed"] = len(df)
print(f"  Time features recomputed from date (all {len(df):,} rows)")

# ── 7. Validate categoricals ──────────────────────────────────────────────────
# season — fix unknown values from month
bad_season = ~df["season"].isin(VALID_SEASONS)
df.loc[bad_season, "season"] = df.loc[bad_season, "month"].map(SEASON_MAP)
report["season_fixed"] = int(bad_season.sum())
print(f"  season values fixed           : {report['season_fixed']:,}")

# gender — unknown → 'Unisex'
bad_gender = ~df["gender"].isin(VALID_GENDERS)
df.loc[bad_gender, "gender"] = "Unisex"
report["gender_fixed"] = int(bad_gender.sum())
print(f"  gender values fixed           : {report['gender_fixed']:,}")

# promotion_type — blank when promotion=0 should be 'No Promotion'
mask_no_promo = (df["promotion"] == 0) & (df["promotion_type"].str.strip() == "")
df.loc[mask_no_promo, "promotion_type"] = "No Promotion"
report["promotion_type_fixed"] = int(mask_no_promo.sum())
print(f"  promotion_type blanks fixed   : {report['promotion_type_fixed']:,}")

# ── 8. Remove non-positive quantity ──────────────────────────────────────────
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
before = len(df)
df = df[df["quantity"] > 0].copy()
report["non_positive_qty_dropped"] = before - len(df)
print(f"  Non-positive quantity dropped : {report['non_positive_qty_dropped']:,}")

# ── 9. Remove negative prices ────────────────────────────────────────────────
for col in ["unit_price", "cost_price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
before = len(df)
df = df[(df["unit_price"] > 0) & (df["cost_price"] >= 0)].copy()
report["negative_price_dropped"] = before - len(df)
print(f"  Negative price rows dropped   : {report['negative_price_dropped']:,}")

# ── 10. Remove cost_price >= unit_price ───────────────────────────────────────
before = len(df)
df = df[df["cost_price"] < df["unit_price"]].copy()
report["cost_gte_price_dropped"] = before - len(df)
print(f"  cost>=unit_price rows dropped : {report['cost_gte_price_dropped']:,}")

# ── 11. Clip discount_percent to [0, 100] ────────────────────────────────────
df["discount_percent"] = pd.to_numeric(df["discount_percent"], errors="coerce").fillna(0)
bad_disc = ((df["discount_percent"] < 0) | (df["discount_percent"] > 100)).sum()
df["discount_percent"] = df["discount_percent"].clip(0, 100)
report["discount_clipped"] = int(bad_disc)
print(f"  discount_percent clipped      : {report['discount_clipped']:,}")

# ── 12. Recompute derived columns ─────────────────────────────────────────────
df["discount_amount"] = (df["quantity"] * df["unit_price"] * df["discount_percent"] / 100).round(2)
df["total_sales"]     = (df["quantity"] * df["unit_price"] - df["discount_amount"]).round(2)
df["profit"]          = (df["total_sales"] - df["quantity"] * df["cost_price"]).round(2)
print(f"  Derived columns recomputed    : discount_amount, total_sales, profit")

# ── 13. Outlier removal on quantity (IQR per product) ────────────────────────
before = len(df)
q1  = df.groupby("product_id")["quantity"].transform(lambda x: x.quantile(0.25))
q3  = df.groupby("product_id")["quantity"].transform(lambda x: x.quantile(0.75))
iqr = q3 - q1
lower = q1 - 3 * iqr      # 3×IQR — conservative, keeps genuine demand spikes
upper = q3 + 3 * iqr
df = df[(df["quantity"] >= lower) & (df["quantity"] <= upper)].copy()
report["outlier_qty_dropped"] = before - len(df)
print(f"  Quantity outliers dropped     : {report['outlier_qty_dropped']:,}")

# ── 14. Reset index & format date back to string ─────────────────────────────
df.reset_index(drop=True, inplace=True)
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

# ── 15. Save ──────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT, index=False)
final_rows = len(df)

print("\n" + "="*55)
print("  DATA CLEANING SUMMARY")
print("="*55)
print(f"  Input file          : {INPUT}")
print(f"  Output file         : {OUTPUT}")
print(f"  Initial rows        : {initial_rows:,}")
print(f"  Final rows          : {final_rows:,}")
print(f"  Total rows removed  : {initial_rows - final_rows:,}")
print(f"  Retention rate      : {100 * final_rows / initial_rows:.2f}%")
print("="*55)
for k, v in report.items():
    print(f"  {k:<35}: {v:,}")
print("="*55)
print(f"\nCleaned dataset saved to '{OUTPUT}'")
