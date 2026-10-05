"""test_engine.py — run from backend/ to verify the new engine"""
import django, os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from sales.models import Sale
from django.db.models import Count
from django.conf import settings
from ml.engine import train_and_evaluate, forecast_future, _aggregate_daily

MODELS_DIR = str(settings.ML_MODELS_DIR)

# Find the shop+product combo with the most unique dates
print("Finding best combo for testing...")
top = (Sale.objects
       .values('shop_id', 'product_id', 'product__name')
       .annotate(n=Count('id'))
       .order_by('-n')[:1])

if not top:
    print("No sales data in DB. Upload the Thakur Footwear CSV first.")
    sys.exit(1)

t = top[0]
SHOP_ID    = t['shop_id']
PRODUCT_ID = t['product_id']
print(f"Using shop_id={SHOP_ID}, product_id={PRODUCT_ID}, product={t['product__name']}, rows={t['n']}")

sales_qs = Sale.objects.filter(shop_id=SHOP_ID, product_id=PRODUCT_ID)
daily = _aggregate_daily(sales_qs)
print(f"Daily aggregated records: {len(daily)}")
if len(daily) > 0:
    qtys = daily['quantity'].values
    print(f"Daily qty — min={qtys.min():.1f}  max={qtys.max():.1f}  mean={qtys.mean():.1f}  std={qtys.std():.1f}")

print("\n--- Training LSTM ---")
try:
    r = train_and_evaluate(sales_qs, SHOP_ID, PRODUCT_ID, 'LSTM', MODELS_DIR)
    print(f"  Total days : {r['total_days']}  (train={r['train_days']}  test={r['test_days']})")
    print(f"  MAE  : {r['mae']:.4f}")
    print(f"  RMSE : {r['rmse']:.4f}")
    print(f"  R2   : {r['r2']:.4f}  {'GOOD' if r['r2'] > 0.5 else 'OK' if r['r2'] > 0 else 'needs more data'}")
    print(f"  Actual  (first 5): {[round(v,1) for v in r['actual'][:5]]}")
    print(f"  Predicted (first 5): {[round(v,1) for v in r['predicted'][:5]]}")
except ValueError as e:
    print(f"  ERROR: {e}")

print("\n--- Training GRU ---")
try:
    r = train_and_evaluate(sales_qs, SHOP_ID, PRODUCT_ID, 'GRU', MODELS_DIR)
    print(f"  MAE  : {r['mae']:.4f}")
    print(f"  RMSE : {r['rmse']:.4f}")
    print(f"  R2   : {r['r2']:.4f}  {'GOOD' if r['r2'] > 0.5 else 'OK' if r['r2'] > 0 else 'needs more data'}")
except ValueError as e:
    print(f"  ERROR: {e}")

print("\n--- Forecast 30 days ---")
try:
    fc = forecast_future(sales_qs, SHOP_ID, PRODUCT_ID, 'LSTM', 30, MODELS_DIR)
    print(f"  Forecast entries: {len(fc)}")
    print(f"  First 5: {[(d, round(q,1)) for d,q in fc[:5]]}")
    print(f"  All positive: {all(q >= 0 for _,q in fc)}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\nDone.")
