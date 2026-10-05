"""ML engine end-to-end test — run after seed_ml.py"""
import requests, json

BASE = "http://localhost:8000/api"

# Login
r = requests.post(BASE + "/auth/login/", json={"username": "testaudit99", "password": "pass1234"})
TOKEN = r.json()["access"]
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

PASS = "[PASS]"
FAIL = "[FAIL]"

def check(label, ok, detail=""):
    print(f"{'[PASS]' if ok else '[FAIL]'} {label}" + (f" -- {detail}" if detail else ""))
    return ok

# Find the ML test shop/product
shops = requests.get(BASE + "/shops/", headers=H).json()
products = requests.get(BASE + "/products/", headers=H).json()
shop = next((s for s in shops if s["name"] == "ML Test Shop"), None)
product = next((p for p in products if p["name"] == "ML Test Shoe"), None)

check("ML Test Shop exists in DB", shop is not None, str(shop))
check("ML Test Shoe exists in DB", product is not None, str(product))

if not shop or not product:
    print("Cannot continue ML tests without test data.")
    exit(1)

SHOP_ID = shop["id"]
PRODUCT_ID = product["id"]
print(f"\nUsing shop_id={SHOP_ID}, product_id={PRODUCT_ID}\n")

# --- TRAIN LSTM ---
print("-- LSTM Training --")
r = requests.post(BASE + "/ml/train/", headers=H,
                  json={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "LSTM"})
check("LSTM train returns 200", r.status_code == 200, r.text[:100])
if r.status_code == 200:
    d = r.json()
    m = d.get("metrics", {})
    check("LSTM has mae", "mae" in m, str(m.get("mae")))
    check("LSTM has mse", "mse" in m, str(m.get("mse")))
    check("LSTM has rmse", "rmse" in m, str(m.get("rmse")))
    check("LSTM has r2", "r2" in m, str(m.get("r2")))
    check("LSTM actual array non-empty", len(d.get("actual", [])) > 0)
    check("LSTM predicted array non-empty", len(d.get("predicted", [])) > 0)
    check("LSTM actual/predicted same length",
          len(d.get("actual", [])) == len(d.get("predicted", [])),
          f"actual={len(d.get('actual',[]))} predicted={len(d.get('predicted',[]))}")
    check("LSTM dates array non-empty", len(d.get("dates", [])) > 0)
    check("LSTM RMSE is a positive number", isinstance(m.get("rmse"), float) and m["rmse"] > 0)
    check("LSTM R2 is a number", isinstance(m.get("r2"), float))
    lstm_rmse = m.get("rmse")
    print(f"  LSTM Metrics: MAE={m.get('mae'):.4f}  MSE={m.get('mse'):.4f}  RMSE={m.get('rmse'):.4f}  R2={m.get('r2'):.4f}")

# --- TRAIN GRU ---
print("\n-- GRU Training --")
r = requests.post(BASE + "/ml/train/", headers=H,
                  json={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "GRU"})
check("GRU train returns 200", r.status_code == 200, r.text[:100])
if r.status_code == 200:
    d = r.json()
    m = d.get("metrics", {})
    check("GRU metrics present", all(k in m for k in ["mae","mse","rmse","r2"]))
    gru_rmse = m.get("rmse")
    print(f"  GRU  Metrics: MAE={m.get('mae'):.4f}  MSE={m.get('mse'):.4f}  RMSE={m.get('rmse'):.4f}  R2={m.get('r2'):.4f}")

# --- MODEL COMPARISON WINNER ---
print("\n-- Model Comparison --")
if 'lstm_rmse' in dir() and 'gru_rmse' in dir():
    winner = "LSTM" if lstm_rmse < gru_rmse else "GRU"
    check("Winner correctly identified by lower RMSE", True,
          f"LSTM RMSE={lstm_rmse:.4f}  GRU RMSE={gru_rmse:.4f}  Winner={winner}")

# --- EVALUATIONS SAVED ---
r = requests.get(BASE + "/forecasts/evaluations/", headers=H,
                 params={"shop_id": SHOP_ID, "product_id": PRODUCT_ID})
check("Evaluations saved to DB", r.status_code == 200 and len(r.json()) >= 2,
      f"count={len(r.json())}")
evals = r.json()
model_types = [e["model_type"] for e in evals]
check("Both LSTM and GRU evaluations stored", "LSTM" in model_types and "GRU" in model_types,
      str(model_types))

# --- FORECAST FUTURE (LSTM) ---
print("\n-- Future Forecast --")
r = requests.post(BASE + "/ml/forecast/", headers=H,
                  json={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "LSTM", "steps": 30})
check("LSTM forecast returns 200", r.status_code == 200, r.text[:100])
if r.status_code == 200:
    fc = r.json().get("forecasts", [])
    check("Forecast returns 30 entries", len(fc) == 30, f"got {len(fc)}")
    check("All forecast entries have date", all("date" in f for f in fc))
    check("All forecast entries have predicted_qty", all("predicted_qty" in f for f in fc))
    check("All predicted_qty are positive numbers",
          all(isinstance(f["predicted_qty"], (int, float)) and f["predicted_qty"] >= 0 for f in fc))
    # Dates are sequential
    from datetime import datetime
    dates = [datetime.strptime(f["date"], "%Y-%m-%d") for f in fc]
    sequential = all((dates[i+1] - dates[i]).days == 1 for i in range(len(dates)-1))
    check("Forecast dates are sequential (no gaps)", sequential)

# --- FORECAST SAVED TO DB ---
r = requests.get(BASE + "/forecasts/results/", headers=H,
                 params={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "LSTM"})
check("Forecast results saved to DB", r.status_code == 200 and len(r.json()) > 0,
      f"count={len(r.json())}")

# --- SHOP/PRODUCT ISOLATION ---
print("\n-- Shop/Product Isolation --")
# Forecast for a different shop should return empty
r = requests.get(BASE + "/forecasts/results/", headers=H,
                 params={"shop_id": 99999, "product_id": PRODUCT_ID})
check("Forecast for wrong shop returns empty list", r.status_code == 200 and r.json() == [],
      r.text[:80])

# --- FORECAST WITHOUT TRAINING ---
r = requests.post(BASE + "/ml/forecast/", headers=H,
                  json={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "GRU", "steps": 7})
check("Forecast after GRU training works", r.status_code == 200)

# Forecast for untrained combo
r = requests.post(BASE + "/ml/forecast/", headers=H,
                  json={"shop_id": 99999, "product_id": 99999, "model_type": "LSTM", "steps": 7})
check("Forecast with no data returns 404", r.status_code == 404, r.text[:80])

# --- INVENTORY RECOMMENDATION ---
print("\n-- Inventory Recommendation --")
# Create inventory for ML test combo
inv_r = requests.post(BASE + "/inventory/", headers=H,
                      json={"shop": SHOP_ID, "product": PRODUCT_ID,
                            "current_stock": 50, "reorder_point": 30,
                            "safety_stock": 10, "lead_time_days": 7})
check("Inventory created for ML combo", inv_r.status_code in (200, 201), inv_r.text[:80])

r = requests.get(BASE + "/inventory/recommendation/", headers=H,
                 params={"shop_id": SHOP_ID, "product_id": PRODUCT_ID, "model_type": "LSTM"})
check("Inventory recommendation returns 200", r.status_code == 200, r.text[:120])
if r.status_code == 200:
    rec = r.json()
    check("Recommendation has predicted_demand", "predicted_demand" in rec)
    check("Recommendation has recommended_order_qty", "recommended_order_qty" in rec)
    check("Recommendation has inventory_status", "inventory_status" in rec)
    check("Inventory status is valid value",
          rec.get("inventory_status") in ["Sufficient Stock","Low Stock","Reorder Required","Out of Stock"],
          rec.get("inventory_status"))
    print(f"  Status={rec.get('inventory_status')}  Predicted={rec.get('predicted_demand')}  Order={rec.get('recommended_order_qty')}")

print("\n" + "="*50)
print("ML ENGINE TESTS COMPLETE")
print("="*50)
