"""verify_dataset.py — validates thakur_footwear_sales_500k.csv"""
import csv
from collections import Counter, defaultdict

FILE = "thakur_footwear_sales_500k.csv"
print(f"Loading {FILE} ...")

rows = []
with open(FILE, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

total = len(rows)
print(f"Total rows: {total:,}\n")

# Weekend vs weekday
wkend = sum(1 for r in rows if r["is_weekend"] == "1")
wkday = total - wkend
print("=== Weekend vs Weekday ===")
print(f"  Weekend txns : {wkend:,}  ({100*wkend/total:.1f}%)")
print(f"  Weekday txns : {wkday:,}  ({100*wkday/total:.1f}%)")
print(f"  Ratio        : {wkend/max(wkday,1):.2f}x  (expect >1.0)")

# Festival vs normal
fest = sum(1 for r in rows if r["is_holiday"] == "1")
norm = total - fest
print("\n=== Festival vs Normal ===")
print(f"  Festival txns : {fest:,}  ({100*fest/total:.1f}%)")
print(f"  Normal txns   : {norm:,}  ({100*norm/total:.1f}%)")

# Season breakdown
seasons = Counter(r["season"] for r in rows)
print("\n=== Season Breakdown ===")
for s, c in seasons.most_common():
    print(f"  {s:10s}: {c:,}  ({100*c/total:.1f}%)")

# Category breakdown
cats = Counter(r["category"] for r in rows)
print("\n=== Category Breakdown ===")
for c, n in cats.most_common():
    print(f"  {c:22s}: {n:,}")

# School shoes by month
school = [r for r in rows if r["category"] == "School Shoes"]
school_months = Counter(r["month"] for r in school)
print("\n=== School Shoes by Month ===")
for m in sorted(school_months, key=int):
    bar = "#" * (school_months[m] // 200)
    print(f"  Month {int(m):2d}: {school_months[m]:6,}  {bar}")

# Sandals by season
sandals = [r for r in rows if r["category"] == "Sandals"]
sandal_seasons = Counter(r["season"] for r in sandals)
print("\n=== Sandals by Season (expect Summer highest) ===")
for s, c in sandal_seasons.most_common():
    print(f"  {s}: {c:,}")

# Boots by season
boots = [r for r in rows if r["category"] == "Boots"]
boot_seasons = Counter(r["season"] for r in boots)
print("\n=== Boots by Season (expect Winter/Monsoon highest) ===")
for s, c in boot_seasons.most_common():
    print(f"  {s}: {c:,}")

# Promotion impact
promo    = [r for r in rows if r["promotion"] == "1"]
no_promo = [r for r in rows if r["promotion"] == "0"]
avg_qty_promo = sum(float(r["quantity"]) for r in promo) / max(len(promo), 1)
avg_qty_norm  = sum(float(r["quantity"]) for r in no_promo) / max(len(no_promo), 1)
print("\n=== Promotion Impact ===")
print(f"  Promo txns    : {len(promo):,}  avg qty/txn = {avg_qty_promo:.2f}")
print(f"  No-promo txns : {len(no_promo):,}  avg qty/txn = {avg_qty_norm:.2f}")

# Top 5 products
prod_cnt = Counter(r["product_name"] for r in rows)
print("\n=== Top 5 Products by Transactions ===")
for p, c in prod_cnt.most_common(5):
    print(f"  {p}: {c:,}")

# Bottom 5 products
print("\n=== Bottom 5 Products (slow movers) ===")
for p, c in prod_cnt.most_common()[:-6:-1]:
    print(f"  {p}: {c:,}")

# Diwali window
diwali = [r for r in rows if r["holiday_name"] == "Diwali"]
print(f"\n=== Diwali transactions: {len(diwali):,} ===")

# Data quality checks
neg_price = sum(1 for r in rows if float(r["unit_price"]) < 0 or float(r["cost_price"]) < 0)
bad_disc  = sum(1 for r in rows if not (0 <= float(r["discount_percent"]) <= 100))
cost_gte  = sum(1 for r in rows if float(r["cost_price"]) >= float(r["unit_price"]))
neg_qty   = sum(1 for r in rows if float(r["quantity"]) <= 0)
wrong_rev = sum(1 for r in rows
                if abs(float(r["total_sales"]) -
                       (float(r["quantity"]) * float(r["unit_price"]) *
                        (1 - float(r["discount_percent"]) / 100))) > 0.05)
print("\n=== Data Quality ===")
print(f"  Negative prices     : {neg_price}  (expect 0)")
print(f"  Bad discounts       : {bad_disc}   (expect 0)")
print(f"  Cost >= unit price  : {cost_gte}   (expect 0)")
print(f"  Non-positive qty    : {neg_qty}    (expect 0)")
print(f"  Revenue calc errors : {wrong_rev}  (expect 0)")

# LSTM readiness — daily aggregated records per product
prod_dates = defaultdict(set)
for r in rows:
    prod_dates[r["product_id"]].add(r["date"])
min_days = min(len(v) for v in prod_dates.values())
max_days = max(len(v) for v in prod_dates.values())
print("\n=== LSTM Readiness (daily aggregated records per product) ===")
print(f"  Min days with sales : {min_days}  (need >= 15)")
print(f"  Max days with sales : {max_days}")
print(f"  All products LSTM-ready: {min_days >= 15}")

# Unique shops
shops = Counter(r["shop_id"] for r in rows)
print(f"\n=== Shops: {dict(shops)} (expect only TF001) ===")

# Date range
dates = sorted(set(r["date"] for r in rows))
print(f"\n=== Date range: {dates[0]} to {dates[-1]}  ({len(dates)} unique dates) ===")

# Revenue summary
total_rev = sum(float(r["total_sales"]) for r in rows)
total_profit = sum(float(r["profit"]) for r in rows)
print(f"\n=== Financials ===")
print(f"  Total Revenue : Rs {total_rev:,.0f}")
print(f"  Total Profit  : Rs {total_profit:,.0f}")
print(f"  Margin        : {100*total_profit/max(total_rev,1):.1f}%")

print("\n=== OVERALL VALIDATION ===")
ok = (
    abs(total - 500_000) / 500_000 < 0.05
    and len(dates) == 365
    and len(shops) == 1
    and neg_price == 0
    and bad_disc == 0
    and cost_gte == 0
    and neg_qty == 0
    and min_days >= 15
)
print(f"  RESULT: {'PASSED' if ok else 'FAILED'}")
