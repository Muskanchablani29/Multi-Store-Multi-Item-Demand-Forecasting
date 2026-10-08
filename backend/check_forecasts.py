import pymysql

conn = pymysql.connect(host='localhost', user='root', password='muskan123', database='demand_forecasting')
cur = conn.cursor()

print("=== FORECASTS in DB ===")
cur.execute("SELECT shop_id, product_id, model_type, MIN(forecast_date), MAX(forecast_date), COUNT(*) FROM forecasts_forecast GROUP BY shop_id, product_id, model_type LIMIT 10")
for row in cur.fetchall():
    print(f"  shop={row[0]} product={row[1]} type={row[2]} from={row[3]} to={row[4]} count={row[5]}")

print("\n=== Total forecast rows ===")
cur.execute("SELECT COUNT(*) FROM forecasts_forecast")
print(" ", cur.fetchone()[0])

from datetime import date
today = date.today()
next_month = today.month % 12 + 1
next_year  = today.year if next_month > 1 else today.year + 1
print(f"\n=== Dashboard looks for: year={next_year} month={next_month} ===")

cur.execute("SELECT COUNT(*) FROM forecasts_forecast WHERE YEAR(forecast_date)=%s AND MONTH(forecast_date)=%s", (next_year, next_month))
print(f"  Matching rows: {cur.fetchone()[0]}")

cur.close()
conn.close()
