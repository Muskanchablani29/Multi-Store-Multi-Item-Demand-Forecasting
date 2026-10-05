import csv
from collections import defaultdict

daily = defaultdict(lambda: {"txns": 0, "is_weekend": 0})
with open("thakur_footwear_sales_500k.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        daily[r["date"]]["txns"] += 1
        daily[r["date"]]["is_weekend"] = int(r["is_weekend"])

weekend_days = [v["txns"] for v in daily.values() if v["is_weekend"] == 1]
weekday_days = [v["txns"] for v in daily.values() if v["is_weekend"] == 0]

avg_wkend = sum(weekend_days) / len(weekend_days)
avg_wkday = sum(weekday_days) / len(weekday_days)

print(f"Weekend days         : {len(weekend_days)}")
print(f"Weekday days         : {len(weekday_days)}")
print(f"Avg txns/weekend day : {avg_wkend:.1f}")
print(f"Avg txns/weekday day : {avg_wkday:.1f}")
print(f"Per-day ratio        : {avg_wkend/avg_wkday:.2f}x  (expect >1.0)")

# Top 5 highest-sales days
top = sorted(daily.items(), key=lambda x: x[1]["txns"], reverse=True)[:5]
print("\nTop 5 highest-sales days:")
for d, v in top:
    tag = "WEEKEND" if v["is_weekend"] else "weekday"
    print(f"  {d}  {v['txns']:,} txns  [{tag}]")
