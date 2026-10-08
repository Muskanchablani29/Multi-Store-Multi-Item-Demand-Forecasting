import pymysql

conn = pymysql.connect(host='localhost', user='root', password='muskan123', database='demand_forecasting')
cur = conn.cursor()

# Update shop name
cur.execute("UPDATE shops_shop SET name='StepStyle Footwear', shop_id='SS001' WHERE name='Thakur Footwear'")
conn.commit()

# Verify
cur.execute("SELECT id, name, shop_id, owner_id FROM shops_shop")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
print("Done.")
