import pymysql
import random
from datetime import date, timedelta

conn = pymysql.connect(host='localhost', user='root', password='muskan123', database='demand_forecasting')
cur = conn.cursor()

# ── 1. Rename shops ──────────────────────────────────────────────────────────
cur.execute("UPDATE shops_shop SET name='StepStyle Footwear', shop_id='SS001' WHERE owner_id=(SELECT id FROM auth_user WHERE username='muskan')")
cur.execute("UPDATE shops_shop SET name='Trend Fashion', shop_id='TF001', category='Clothing' WHERE owner_id=(SELECT id FROM auth_user WHERE username='ritesh')")
cur.execute("UPDATE shops_shop SET name='Priya Fresh Mart', shop_id='PF001', category='Grocery' WHERE owner_id=(SELECT id FROM auth_user WHERE username='priya')")
conn.commit()

cur.execute("SELECT id, name, shop_id, category, owner_id FROM shops_shop")
shops = {row[4]: (row[0], row[1], row[2], row[3]) for row in cur.fetchall()}
print("Shops:", shops)

cur.execute("SELECT id FROM auth_user WHERE username='ritesh'")
ritesh_uid = cur.fetchone()[0]
cur.execute("SELECT id FROM auth_user WHERE username='priya'")
priya_uid = cur.fetchone()[0]

ritesh_shop_id = shops[ritesh_uid][0]
priya_shop_id  = shops[priya_uid][0]
print(f"Ritesh shop id: {ritesh_shop_id}, Priya shop id: {priya_shop_id}")

# ── 2. Clothing products for Ritesh (Trend Fashion) ─────────────────────────
CLOTHING = [
    ('TF-P001','Levis Slim Fit Jeans',       'Jeans',       'Slim Fit',    'Levis',       'Men',   1299, 700),
    ('TF-P002','Levis Regular Fit Jeans',     'Jeans',       'Regular Fit', 'Levis',       'Men',   1199, 650),
    ('TF-P003','Wrangler Straight Jeans',     'Jeans',       'Straight',    'Wrangler',    'Men',   1099, 580),
    ('TF-P004','H&M Women Skinny Jeans',      'Jeans',       'Skinny',      'H&M',         'Women', 999,  520),
    ('TF-P005','Zara Women Flare Jeans',      'Jeans',       'Flare',       'Zara',        'Women', 1499, 800),
    ('TF-P006','Allen Solly Formal Shirt',    'Shirts',      'Formal',      'Allen Solly', 'Men',   899,  450),
    ('TF-P007','Van Heusen Formal Shirt',     'Shirts',      'Formal',      'Van Heusen',  'Men',   999,  500),
    ('TF-P008','Peter England Casual Shirt',  'Shirts',      'Casual',      'Peter England','Men',  799,  400),
    ('TF-P009','H&M Women Floral Shirt',      'Shirts',      'Casual',      'H&M',         'Women', 699,  350),
    ('TF-P010','Zara Women Formal Blouse',    'Shirts',      'Formal',      'Zara',        'Women', 1199, 600),
    ('TF-P011','Nike Dri-Fit T-Shirt',        'T-Shirts',    'Sports',      'Nike',        'Men',   599,  280),
    ('TF-P012','Adidas Trefoil T-Shirt',      'T-Shirts',    'Casual',      'Adidas',      'Men',   699,  320),
    ('TF-P013','Puma Essential T-Shirt',      'T-Shirts',    'Casual',      'Puma',        'Men',   499,  240),
    ('TF-P014','H&M Women Basic T-Shirt',     'T-Shirts',    'Casual',      'H&M',         'Women', 399,  180),
    ('TF-P015','Zara Women Graphic Tee',      'T-Shirts',    'Casual',      'Zara',        'Women', 799,  380),
    ('TF-P016','Raymond Wool Blazer',         'Blazers',     'Formal',      'Raymond',     'Men',   3999, 2200),
    ('TF-P017','Van Heusen Slim Blazer',      'Blazers',     'Slim Fit',    'Van Heusen',  'Men',   3499, 1900),
    ('TF-P018','Zara Women Office Blazer',    'Blazers',     'Formal',      'Zara',        'Women', 2999, 1600),
    ('TF-P019','H&M Women Casual Blazer',     'Blazers',     'Casual',      'H&M',         'Women', 1999, 1000),
    ('TF-P020','Nike Track Pants',            'Track Pants', 'Sports',      'Nike',        'Men',   999,  480),
    ('TF-P021','Adidas Tiro Track Pants',     'Track Pants', 'Sports',      'Adidas',      'Men',   1099, 520),
    ('TF-P022','Puma Women Track Pants',      'Track Pants', 'Sports',      'Puma',        'Women', 899,  420),
    ('TF-P023','H&M Women Joggers',           'Track Pants', 'Casual',      'H&M',         'Women', 799,  380),
    ('TF-P024','Manyavar Kurta',              'Ethnic Wear', 'Kurta',       'Manyavar',    'Men',   1499, 800),
    ('TF-P025','Biba Women Kurti',            'Ethnic Wear', 'Kurti',       'Biba',        'Women', 999,  500),
    ('TF-P026','W Women Salwar Suit',         'Ethnic Wear', 'Salwar Suit', 'W',           'Women', 1799, 950),
    ('TF-P027','Fabindia Cotton Kurta',       'Ethnic Wear', 'Kurta',       'Fabindia',    'Men',   1299, 680),
    ('TF-P028','Libas Women Anarkali',        'Ethnic Wear', 'Anarkali',    'Libas',       'Women', 1599, 850),
    ('TF-P029','Woodland Winter Jacket',      'Jackets',     'Winter',      'Woodland',    'Men',   2999, 1600),
    ('TF-P030','Levis Denim Jacket',          'Jackets',     'Casual',      'Levis',       'Men',   2499, 1300),
    ('TF-P031','H&M Women Puffer Jacket',     'Jackets',     'Winter',      'H&M',         'Women', 1999, 1000),
    ('TF-P032','Zara Women Trench Coat',      'Jackets',     'Formal',      'Zara',        'Women', 3499, 1900),
    ('TF-P033','Allen Solly Chinos',          'Trousers',    'Chinos',      'Allen Solly', 'Men',   1199, 600),
    ('TF-P034','Van Heusen Formal Trousers',  'Trousers',    'Formal',      'Van Heusen',  'Men',   1299, 680),
    ('TF-P035','H&M Women Palazzo',           'Trousers',    'Casual',      'H&M',         'Women', 899,  420),
    ('TF-P036','Zara Women Formal Trousers',  'Trousers',    'Formal',      'Zara',        'Women', 1499, 780),
    ('TF-P037','Jockey Men Innerwear Set',    'Innerwear',   'Set',         'Jockey',      'Men',   599,  280),
    ('TF-P038','Jockey Women Innerwear Set',  'Innerwear',   'Set',         'Jockey',      'Women', 699,  320),
    ('TF-P039','Dollar Men Vest Pack',        'Innerwear',   'Vest',        'Dollar',      'Men',   299,  130),
    ('TF-P040','Enamor Women Bra',            'Innerwear',   'Bra',         'Enamor',      'Women', 499,  220),
]

# ── 3. Grocery products for Priya (Priya Fresh Mart) ────────────────────────
GROCERY = [
    ('PF-P001','Aashirvaad Atta 10kg',        'Grains & Flour',  'Atta',        'Aashirvaad',  'Unisex', 320,  260),
    ('PF-P002','India Gate Basmati Rice 5kg', 'Grains & Flour',  'Rice',        'India Gate',  'Unisex', 450,  370),
    ('PF-P003','Tata Salt 1kg',               'Spices & Salt',   'Salt',        'Tata',        'Unisex', 28,   20),
    ('PF-P004','Catch Black Pepper 100g',     'Spices & Salt',   'Spices',      'Catch',       'Unisex', 85,   60),
    ('PF-P005','MDH Garam Masala 100g',       'Spices & Salt',   'Masala',      'MDH',         'Unisex', 75,   52),
    ('PF-P006','Amul Butter 500g',            'Dairy',           'Butter',      'Amul',        'Unisex', 250,  210),
    ('PF-P007','Amul Milk 1L',                'Dairy',           'Milk',        'Amul',        'Unisex', 62,   52),
    ('PF-P008','Mother Dairy Curd 400g',      'Dairy',           'Curd',        'Mother Dairy','Unisex', 45,   36),
    ('PF-P009','Amul Cheese Slices 200g',     'Dairy',           'Cheese',      'Amul',        'Unisex', 120,  95),
    ('PF-P010','Britannia Bread 400g',        'Bakery',          'Bread',       'Britannia',   'Unisex', 45,   34),
    ('PF-P011','Britannia Good Day Biscuits', 'Snacks',          'Biscuits',    'Britannia',   'Unisex', 35,   24),
    ('PF-P012','Parle-G Biscuits 800g',       'Snacks',          'Biscuits',    'Parle',       'Unisex', 80,   58),
    ('PF-P013','Lays Classic Chips 26g',      'Snacks',          'Chips',       'Lays',        'Unisex', 20,   13),
    ('PF-P014','Kurkure Masala Munch 90g',    'Snacks',          'Chips',       'Kurkure',     'Unisex', 30,   20),
    ('PF-P015','Maggi Noodles 70g',           'Instant Food',    'Noodles',     'Maggi',       'Unisex', 14,   9),
    ('PF-P016','Yippee Noodles 70g',          'Instant Food',    'Noodles',     'Yippee',      'Unisex', 14,   9),
    ('PF-P017','Knorr Soup Tomato 44g',       'Instant Food',    'Soup',        'Knorr',       'Unisex', 35,   24),
    ('PF-P018','Tata Tea Premium 500g',       'Beverages',       'Tea',         'Tata Tea',    'Unisex', 220,  175),
    ('PF-P019','Nescafe Classic 50g',         'Beverages',       'Coffee',      'Nescafe',     'Unisex', 180,  140),
    ('PF-P020','Tropicana Orange Juice 1L',   'Beverages',       'Juice',       'Tropicana',   'Unisex', 120,  90),
    ('PF-P021','Coca Cola 2L',                'Beverages',       'Cold Drinks', 'Coca Cola',   'Unisex', 95,   70),
    ('PF-P022','Pepsi 2L',                    'Beverages',       'Cold Drinks', 'Pepsi',       'Unisex', 90,   68),
    ('PF-P023','Fortune Sunflower Oil 1L',    'Oils & Ghee',     'Oil',         'Fortune',     'Unisex', 140,  115),
    ('PF-P024','Patanjali Desi Ghee 1kg',     'Oils & Ghee',     'Ghee',        'Patanjali',   'Unisex', 550,  460),
    ('PF-P025','Surf Excel Detergent 1kg',    'Household',       'Detergent',   'Surf Excel',  'Unisex', 220,  175),
    ('PF-P026','Ariel Detergent 1kg',         'Household',       'Detergent',   'Ariel',       'Unisex', 240,  190),
    ('PF-P027','Vim Dishwash Bar 200g',       'Household',       'Dishwash',    'Vim',         'Unisex', 30,   20),
    ('PF-P028','Colgate Toothpaste 200g',     'Personal Care',   'Toothpaste',  'Colgate',     'Unisex', 95,   70),
    ('PF-P029','Dove Soap 100g',              'Personal Care',   'Soap',        'Dove',        'Unisex', 55,   38),
    ('PF-P030','Head Shoulders Shampoo 340ml','Personal Care',   'Shampoo',     'Head Shoulders','Unisex',299, 230),
    ('PF-P031','Dettol Handwash 200ml',       'Personal Care',   'Handwash',    'Dettol',      'Unisex', 99,   72),
    ('PF-P032','Toor Dal 1kg',                'Pulses',          'Dal',         'Local',       'Unisex', 130,  105),
    ('PF-P033','Chana Dal 1kg',               'Pulses',          'Dal',         'Local',       'Unisex', 110,  88),
    ('PF-P034','Moong Dal 1kg',               'Pulses',          'Dal',         'Local',       'Unisex', 140,  112),
    ('PF-P035','Tomato 1kg',                  'Vegetables',      'Tomato',      'Fresh',       'Unisex', 40,   28),
    ('PF-P036','Onion 1kg',                   'Vegetables',      'Onion',       'Fresh',       'Unisex', 35,   24),
    ('PF-P037','Potato 1kg',                  'Vegetables',      'Potato',      'Fresh',       'Unisex', 30,   20),
    ('PF-P038','Banana 1 dozen',              'Fruits',          'Banana',      'Fresh',       'Unisex', 50,   35),
    ('PF-P039','Apple 1kg',                   'Fruits',          'Apple',       'Fresh',       'Unisex', 180,  140),
    ('PF-P040','Amul Ice Cream 500ml',        'Frozen',          'Ice Cream',   'Amul',        'Unisex', 150,  115),
]

def insert_products(products, shop_id):
    pid_map = {}
    for p in products:
        pid, name, cat, subcat, brand, gender, unit_price, cost_price = p
        cur.execute("""
            INSERT INTO products_product
            (shop_id, product_id, name, category, subcategory, brand, gender,
             size, color, material, unit_price, cost_price,
             supplier_id, supplier_name, lead_time_days, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'','Mixed','',%s,%s,'SUP001','Wholesale Supplier',5,NOW())
            ON DUPLICATE KEY UPDATE name=VALUES(name), unit_price=VALUES(unit_price)
        """, (shop_id, pid, name, cat, subcat, brand, gender, unit_price, cost_price))
        cur.execute("SELECT id FROM products_product WHERE shop_id=%s AND product_id=%s", (shop_id, pid))
        row = cur.fetchone()
        if row:
            pid_map[pid] = (row[0], unit_price, cost_price, cat)
    conn.commit()
    print(f"  Inserted {len(pid_map)} products for shop_id={shop_id}")
    return pid_map

print("\nInserting Trend Fashion products...")
ritesh_products = insert_products(CLOTHING, ritesh_shop_id)

print("Inserting Priya Fresh Mart products...")
priya_products = insert_products(GROCERY, priya_shop_id)

# ── 4. Generate 1 year sales data ────────────────────────────────────────────
SEASONS = {1:'Winter',2:'Winter',3:'Summer',4:'Summer',5:'Summer',
           6:'Monsoon',7:'Monsoon',8:'Monsoon',9:'Monsoon',
           10:'Festival',11:'Festival',12:'Winter'}

FESTIVALS = {
    (1,26):('Republic Day',True),(3,25):('Holi',True),
    (4,14):('Baisakhi',True),(8,15):('Independence Day',True),
    (10,2):('Gandhi Jayanti',True),(10,12):('Dussehra',True),
    (11,1):('Diwali',True),(11,2):('Diwali',True),(11,3):('Diwali',True),
    (12,25):('Christmas',True),
}

# Demand config per category
CLOTHING_DEMAND = {
    'Jeans':       {'base':4,'weekend':1.4,'festival':2.0,'summer':1.2,'winter':1.1,'monsoon':0.9},
    'Shirts':      {'base':5,'weekend':1.3,'festival':1.8,'summer':1.1,'winter':1.0,'monsoon':0.9},
    'T-Shirts':    {'base':6,'weekend':1.5,'festival':1.6,'summer':1.8,'winter':0.7,'monsoon':1.0},
    'Blazers':     {'base':2,'weekend':1.2,'festival':2.5,'summer':0.8,'winter':1.6,'monsoon':0.8},
    'Track Pants': {'base':4,'weekend':1.4,'festival':1.3,'summer':1.3,'winter':1.1,'monsoon':1.0},
    'Ethnic Wear': {'base':3,'weekend':1.3,'festival':3.5,'summer':1.0,'winter':1.2,'monsoon':0.9},
    'Jackets':     {'base':2,'weekend':1.2,'festival':1.4,'summer':0.4,'winter':2.5,'monsoon':0.6},
    'Trousers':    {'base':4,'weekend':1.3,'festival':1.7,'summer':1.1,'winter':1.0,'monsoon':0.9},
    'Innerwear':   {'base':5,'weekend':1.1,'festival':1.2,'summer':1.2,'winter':1.0,'monsoon':1.0},
}

GROCERY_DEMAND = {
    'Grains & Flour': {'base':8,'weekend':1.2,'festival':1.5,'summer':1.0,'winter':1.1,'monsoon':1.0},
    'Spices & Salt':  {'base':6,'weekend':1.1,'festival':1.4,'summer':1.0,'winter':1.1,'monsoon':1.0},
    'Dairy':          {'base':10,'weekend':1.2,'festival':1.3,'summer':1.1,'winter':1.0,'monsoon':1.0},
    'Bakery':         {'base':8,'weekend':1.3,'festival':1.2,'summer':1.0,'winter':1.1,'monsoon':0.9},
    'Snacks':         {'base':9,'weekend':1.5,'festival':1.8,'summer':1.2,'winter':1.1,'monsoon':1.1},
    'Instant Food':   {'base':10,'weekend':1.3,'festival':1.4,'summer':1.0,'winter':1.2,'monsoon':1.3},
    'Beverages':      {'base':8,'weekend':1.4,'festival':1.6,'summer':1.8,'winter':0.8,'monsoon':0.9},
    'Oils & Ghee':    {'base':5,'weekend':1.1,'festival':1.5,'summer':1.0,'winter':1.1,'monsoon':1.0},
    'Household':      {'base':6,'weekend':1.2,'festival':1.3,'summer':1.1,'winter':1.0,'monsoon':1.1},
    'Personal Care':  {'base':7,'weekend':1.2,'festival':1.4,'summer':1.2,'winter':1.0,'monsoon':1.0},
    'Pulses':         {'base':7,'weekend':1.1,'festival':1.4,'summer':1.0,'winter':1.1,'monsoon':1.0},
    'Vegetables':     {'base':12,'weekend':1.3,'festival':1.2,'summer':1.1,'winter':1.0,'monsoon':0.9},
    'Fruits':         {'base':8,'weekend':1.3,'festival':1.3,'summer':1.3,'winter':0.9,'monsoon':0.8},
    'Frozen':         {'base':4,'weekend':1.4,'festival':1.3,'summer':1.6,'winter':0.7,'monsoon':0.8},
}

def generate_sales(shop_id, product_map, demand_cfg):
    start = date(2024, 1, 1)
    end   = date(2024, 12, 31)
    total = 0
    batch = []
    d = start
    while d <= end:
        month      = d.month
        dow        = d.weekday()
        is_weekend = dow >= 5
        season     = SEASONS[month]
        holiday_name, is_holiday = FESTIVALS.get((month, d.day), ('', False))
        week_number = d.isocalendar()[1]

        for pid, (db_id, unit_price, cost_price, cat) in product_map.items():
            cfg  = demand_cfg.get(cat, {'base':5,'weekend':1.2,'festival':1.5,'summer':1.0,'winter':1.0,'monsoon':1.0})
            base = cfg['base']
            mult = 1.0
            if is_weekend:           mult *= cfg['weekend']
            if is_holiday:           mult *= cfg['festival']
            if season == 'Summer':   mult *= cfg['summer']
            if season == 'Winter':   mult *= cfg['winter']
            if season == 'Monsoon':  mult *= cfg['monsoon']
            if season == 'Festival': mult *= 1.3

            qty = max(1, int(random.gauss(base * mult, base * mult * 0.2)))

            promotion    = random.random() < 0.12
            discount_pct = round(random.choice([5,10,15,20]) if promotion else random.choice([0,0,5]), 1)
            promo_type   = random.choice(['Weekend Deal','Festival Offer','Clearance Sale']) if promotion else 'No Promotion'

            gross       = qty * unit_price
            disc_amt    = gross * discount_pct / 100
            total_sales = gross - disc_amt
            profit      = total_sales - (qty * cost_price)

            batch.append((
                shop_id, db_id, str(d), qty,
                unit_price, cost_price, discount_pct, round(disc_amt,2),
                round(total_sales,2), round(profit,2),
                1 if promotion else 0, promo_type, discount_pct if promotion else 0,
                1 if is_holiday else 0, holiday_name, season,
                dow, 1 if is_weekend else 0, month, week_number
            ))

            if len(batch) >= 3000:
                cur.executemany("""
                    INSERT INTO sales_sale
                    (shop_id,product_id,date,quantity,unit_price,cost_price,
                     discount_percent,discount_amount,total_sales,profit,
                     promotion,promotion_type,promotion_discount,
                     is_holiday,holiday_name,season,
                     day_of_week,is_weekend,month,week_number)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, batch)
                conn.commit()
                total += len(batch)
                batch = []
        d += timedelta(days=1)

    if batch:
        cur.executemany("""
            INSERT INTO sales_sale
            (shop_id,product_id,date,quantity,unit_price,cost_price,
             discount_percent,discount_amount,total_sales,profit,
             promotion,promotion_type,promotion_discount,
             is_holiday,holiday_name,season,
             day_of_week,is_weekend,month,week_number)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, batch)
        conn.commit()
        total += len(batch)
    return total

print("\nGenerating Trend Fashion sales...")
r = generate_sales(ritesh_shop_id, ritesh_products, CLOTHING_DEMAND)
print(f"  {r} rows inserted")

print("Generating Priya Fresh Mart sales...")
p = generate_sales(priya_shop_id, priya_products, GROCERY_DEMAND)
print(f"  {p} rows inserted")

# ── 5. Final summary ─────────────────────────────────────────────────────────
print("\n=== FINAL STATE ===")
cur.execute("SELECT s.name, s.category, COUNT(DISTINCT p.id) as products, COUNT(sa.id) as sales FROM shops_shop s LEFT JOIN products_product p ON p.shop_id=s.id LEFT JOIN sales_sale sa ON sa.shop_id=s.id GROUP BY s.id, s.name, s.category")
for row in cur.fetchall():
    print(f"  {row[0]} ({row[1]}) | Products: {row[2]} | Sales: {row[3]:,}")

cur.close()
conn.close()
print("\nDone!")
