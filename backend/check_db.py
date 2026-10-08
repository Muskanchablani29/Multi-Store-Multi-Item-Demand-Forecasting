import pymysql
import os

conn = pymysql.connect(host='localhost', user='root', password='muskan123', database='demand_forecasting')
cur = conn.cursor()

print("=== PRODUCTS for shop_id=12 (first 10) ===")
cur.execute("SELECT id, name, category, shop_id FROM products_product WHERE shop_id=12 ORDER BY id LIMIT 10")
for row in cur.fetchall():
    print(row)

print("\n=== MODEL EVALUATIONS (all) ===")
cur.execute("SELECT shop_id, product_id, model_type FROM forecasts_modelevaluation ORDER BY product_id")
for row in cur.fetchall():
    print(row)

print("\n=== FORECASTS count per product ===")
cur.execute("SELECT product_id, COUNT(*) FROM forecasts_forecast GROUP BY product_id LIMIT 10")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
