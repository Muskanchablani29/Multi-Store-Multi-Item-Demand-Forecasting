"""
End-to-end API audit test script.
Run from backend/ directory: python test_api.py
"""
import requests
import json
import sys

BASE = "http://localhost:8000/api"
PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
WARN = "\033[93m[WARN]\033[0m"

results = []

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"{status} {label}" + (f" — {detail}" if detail else ""))
    results.append((label, condition, detail))
    return condition

def get(url, token=None, params=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = requests.get(BASE + url, headers=h, params=params, timeout=10)
        return r
    except Exception as e:
        return None

def post(url, data=None, token=None, files=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        if files:
            r = requests.post(BASE + url, headers=h, files=files, timeout=30)
        else:
            h["Content-Type"] = "application/json"
            r = requests.post(BASE + url, headers=h, json=data, timeout=30)
        return r
    except Exception as e:
        return None

def patch(url, data, token):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        return requests.patch(BASE + url, headers=h, json=data, timeout=10)
    except:
        return None

print("\n" + "="*60)
print("  DEMAND FORECASTING — FULL API AUDIT")
print("="*60 + "\n")

# ── 1. AUTH ──────────────────────────────────────────────────
print("── AUTH ──")

# Register (may already exist)
r = post("/auth/register/", {"username": "testaudit99", "email": "t@t.com", "password": "pass1234"})
check("Register new user", r is not None and r.status_code in (200, 201, 400),
      r.text[:80] if r else "no response")

# Duplicate register
r2 = post("/auth/register/", {"username": "testaudit99", "email": "t@t.com", "password": "pass1234"})
check("Duplicate register returns 400", r2 is not None and r2.status_code == 400,
      r2.text[:80] if r2 else "no response")

# Login
r = post("/auth/login/", {"username": "testaudit99", "password": "pass1234"})
check("Login returns 200 with tokens", r is not None and r.status_code == 200 and "access" in (r.json() if r else {}),
      r.text[:80] if r else "no response")

TOKEN = r.json().get("access") if r and r.status_code == 200 else None
REFRESH = r.json().get("refresh") if r and r.status_code == 200 else None
check("Access token received", bool(TOKEN))

# Token refresh
r = post("/auth/refresh/", {"refresh": REFRESH})
check("Token refresh works", r is not None and r.status_code == 200 and "access" in (r.json() if r else {}),
      r.text[:80] if r else "no response")

# Unauthorized access
r = get("/shops/")
check("Unauthenticated request returns 401", r is not None and r.status_code == 401,
      r.text[:80] if r else "no response")

# Bad token
r = get("/shops/", token="badtoken123")
check("Invalid token returns 401", r is not None and r.status_code == 401,
      r.text[:80] if r else "no response")

# ── 2. SHOPS ─────────────────────────────────────────────────
print("\n── SHOPS ──")
r = get("/shops/", token=TOKEN)
check("GET /shops/ returns 200", r is not None and r.status_code == 200)
shops = r.json() if r and r.status_code == 200 else []
check("Shops list is a list", isinstance(shops, list), f"{len(shops)} shops")

r = post("/shops/", {"name": "Audit Test Shop", "location": "Test City"}, token=TOKEN)
check("POST /shops/ creates shop", r is not None and r.status_code == 201, r.text[:80] if r else "")
SHOP_ID = r.json().get("id") if r and r.status_code == 201 else (shops[0]["id"] if shops else None)

# ── 3. PRODUCTS ───────────────────────────────────────────────
print("\n── PRODUCTS ──")
r = get("/products/", token=TOKEN)
check("GET /products/ returns 200", r is not None and r.status_code == 200)
products = r.json() if r and r.status_code == 200 else []
check("Products list is a list", isinstance(products, list), f"{len(products)} products")

r = post("/products/", {"name": "Audit Test Shoe", "category": "Sports", "unit_price": 999}, token=TOKEN)
check("POST /products/ creates product", r is not None and r.status_code == 201, r.text[:80] if r else "")
PRODUCT_ID = r.json().get("id") if r and r.status_code == 201 else (products[0]["id"] if products else None)

# ── 4. SALES ─────────────────────────────────────────────────
print("\n── SALES ──")
r = get("/sales/", token=TOKEN)
check("GET /sales/ returns 200", r is not None and r.status_code == 200)
sales = r.json() if r and r.status_code == 200 else []
check("Sales list is a list", isinstance(sales, list), f"{len(sales)} records")

# Sales stats
r = get("/sales/stats/", token=TOKEN)
check("GET /sales/stats/ returns 200", r is not None and r.status_code == 200)
if r and r.status_code == 200:
    stats = r.json()
    check("Stats has total_revenue", "total_revenue" in stats)
    check("Stats has total_units", "total_units" in stats)
    check("Stats has category_sales", "category_sales" in stats)
    check("Stats has shop_sales", "shop_sales" in stats)
    check("Stats has top_products", "top_products" in stats)

# Sales filter by shop
if SHOP_ID:
    r = get("/sales/", token=TOKEN, params={"shop_id": SHOP_ID})
    check("Sales filter by shop_id works", r is not None and r.status_code == 200)

# CSV upload test
csv_content = b"shop_name,product_name,date,quantity,unit_price,cost_price,discount_percent,promotion,is_holiday,season\nAudit Shop,Audit Shoe,2023-06-01,5,999,600,0,0,0,Summer\nAudit Shop,Audit Shoe,2023-06-02,3,999,600,5,1,0,Summer\nAudit Shop,Audit Shoe,2023-06-03,7,999,600,0,0,1,Summer\n"
r = post("/sales/upload/", token=TOKEN, files={"file": ("test.csv", csv_content, "text/csv")})
check("CSV upload returns 201", r is not None and r.status_code == 201, r.text[:120] if r else "")
if r and r.status_code == 201:
    data = r.json()
    check("CSV upload created records", data.get("created", 0) > 0, f"created={data.get('created')}")

# CSV upload — missing required column
bad_csv = b"shop_name,date\nShop A,2023-01-01\n"
r = post("/sales/upload/", token=TOKEN, files={"file": ("bad.csv", bad_csv, "text/csv")})
check("CSV upload missing columns returns 400", r is not None and r.status_code == 400, r.text[:80] if r else "")

# CSV upload — bad date format
bad_date_csv = b"shop_name,product_name,date,quantity\nShop A,Shoe A,01/06/2023,5\n"
r = post("/sales/upload/", token=TOKEN, files={"file": ("bad_date.csv", bad_date_csv, "text/csv")})
check("CSV upload bad date format caught", r is not None and r.status_code == 201 and len(r.json().get("errors", [])) > 0,
      r.text[:120] if r else "")

# CSV upload — negative quantity
neg_csv = b"shop_name,product_name,date,quantity\nShop A,Shoe A,2023-01-01,-5\n"
r = post("/sales/upload/", token=TOKEN, files={"file": ("neg.csv", neg_csv, "text/csv")})
check("CSV upload negative quantity caught", r is not None and r.status_code == 201 and len(r.json().get("errors", [])) > 0,
      r.text[:120] if r else "")

# ── 5. INVENTORY ─────────────────────────────────────────────
print("\n── INVENTORY ──")
r = get("/inventory/", token=TOKEN)
check("GET /inventory/ returns 200", r is not None and r.status_code == 200)
inventory = r.json() if r and r.status_code == 200 else []
check("Inventory list is a list", isinstance(inventory, list), f"{len(inventory)} items")

# Create inventory item
if SHOP_ID and PRODUCT_ID:
    r = post("/inventory/", {"shop": SHOP_ID, "product": PRODUCT_ID, "current_stock": 100,
                              "reorder_point": 20, "safety_stock": 10, "lead_time_days": 7}, token=TOKEN)
    check("POST /inventory/ creates item", r is not None and r.status_code in (200, 201), r.text[:120] if r else "")
    INV_ID = r.json().get("id") if r and r.status_code in (200, 201) else None

    # Edit inventory
    if INV_ID:
        r = patch(f"/inventory/{INV_ID}/", {"current_stock": 50}, token=TOKEN)
        check("PATCH /inventory/{id}/ updates stock", r is not None and r.status_code == 200,
              r.text[:80] if r else "")

# Reorder alerts
r = get("/inventory/reorder-alerts/", token=TOKEN)
check("GET /inventory/reorder-alerts/ returns 200", r is not None and r.status_code == 200)

# Recommendation — missing params
r = get("/inventory/recommendation/", token=TOKEN)
check("Recommendation without params returns 400", r is not None and r.status_code == 400)

# ── 6. FORECASTS ─────────────────────────────────────────────
print("\n── FORECASTS ──")
r = get("/forecasts/results/", token=TOKEN)
check("GET /forecasts/results/ returns 200", r is not None and r.status_code == 200)

r = get("/forecasts/evaluations/", token=TOKEN)
check("GET /forecasts/evaluations/ returns 200", r is not None and r.status_code == 200)

# Filter forecasts
if SHOP_ID and PRODUCT_ID:
    r = get("/forecasts/results/", token=TOKEN, params={"shop_id": SHOP_ID, "product_id": PRODUCT_ID})
    check("Forecast filter by shop+product works", r is not None and r.status_code == 200)

# ── 7. ML — TRAIN ────────────────────────────────────────────
print("\n── ML ENGINE ──")

# Get a shop+product with enough data
r = get("/sales/", token=TOKEN)
sales_data = r.json() if r and r.status_code == 200 else []

# Find a shop+product combo with enough records
from collections import Counter
combos = Counter((s["shop"], s["product"]) for s in sales_data)
best_combo = combos.most_common(1)

if best_combo and best_combo[0][1] >= 15:
    ML_SHOP = best_combo[0][0][0]
    ML_PRODUCT = best_combo[0][0][1]
    print(f"  Using shop_id={ML_SHOP}, product_id={ML_PRODUCT} ({best_combo[0][1]} records)")

    # Train LSTM
    r = post("/ml/train/", {"shop_id": ML_SHOP, "product_id": ML_PRODUCT, "model_type": "LSTM"}, token=TOKEN)
    check("POST /ml/train/ LSTM returns 200", r is not None and r.status_code == 200, r.text[:120] if r else "")
    if r and r.status_code == 200:
        d = r.json()
        check("LSTM metrics present (mae,mse,rmse,r2)", all(k in d.get("metrics", {}) for k in ["mae","mse","rmse","r2"]))
        check("LSTM actual/predicted arrays returned", "actual" in d and "predicted" in d)
        check("LSTM dates array returned", "dates" in d)
        check("LSTM actual/predicted same length", len(d.get("actual",[])) == len(d.get("predicted",[])))

    # Train GRU
    r = post("/ml/train/", {"shop_id": ML_SHOP, "product_id": ML_PRODUCT, "model_type": "GRU"}, token=TOKEN)
    check("POST /ml/train/ GRU returns 200", r is not None and r.status_code == 200, r.text[:120] if r else "")

    # Forecast
    r = post("/ml/forecast/", {"shop_id": ML_SHOP, "product_id": ML_PRODUCT, "model_type": "LSTM", "steps": 14}, token=TOKEN)
    check("POST /ml/forecast/ returns 200", r is not None and r.status_code == 200, r.text[:120] if r else "")
    if r and r.status_code == 200:
        fc = r.json().get("forecasts", [])
        check("Forecast returns 14 future dates", len(fc) == 14, f"got {len(fc)}")
        check("Forecast entries have date+predicted_qty", all("date" in f and "predicted_qty" in f for f in fc))

    # Forecast without training (wrong model type)
    r = post("/ml/train/", {"shop_id": ML_SHOP, "product_id": ML_PRODUCT, "model_type": "XGB"}, token=TOKEN)
    check("Invalid model_type returns 400", r is not None and r.status_code == 400)

    # Forecast for non-existent shop/product
    r = post("/ml/train/", {"shop_id": 99999, "product_id": 99999, "model_type": "LSTM"}, token=TOKEN)
    check("Train with no data returns 404", r is not None and r.status_code == 404)

else:
    print(f"  {WARN} Not enough sales data for ML tests (need ≥15 records per combo). Upload CSV first.")
    check("ML train test skipped — insufficient data", True, "SKIPPED")

# ── 8. EDGE CASES ────────────────────────────────────────────
print("\n── EDGE CASES ──")

# 404 on non-existent resource
r = get("/shops/99999/", token=TOKEN)
check("GET non-existent shop returns 404", r is not None and r.status_code == 404)

r = get("/inventory/99999/", token=TOKEN)
check("GET non-existent inventory returns 404", r is not None and r.status_code == 404)

# Empty file upload
r = post("/sales/upload/", token=TOKEN, files={"file": ("empty.csv", b"", "text/csv")})
check("Empty CSV upload handled gracefully", r is not None and r.status_code in (400, 201))

# No file upload
r = requests.post(BASE + "/sales/upload/", headers={"Authorization": f"Bearer {TOKEN}"}, timeout=10)
check("Upload with no file returns 400", r is not None and r.status_code == 400)

# ── SUMMARY ──────────────────────────────────────────────────
print("\n" + "="*60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"  RESULTS: {passed} passed / {failed} failed / {len(results)} total")
print("="*60)
if failed:
    print("\nFailed tests:")
    for label, ok, detail in results:
        if not ok:
            print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))
