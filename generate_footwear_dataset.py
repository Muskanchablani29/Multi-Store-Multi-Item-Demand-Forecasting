"""
generate_footwear_dataset.py
Generates a realistic multi-store footwear sales dataset.
Usage: python generate_footwear_dataset.py
Output: footwear_sales_dataset.csv
"""
import csv
import random
import math
from datetime import date, timedelta

random.seed(42)

# ── Configuration ────────────────────────────────────────────────────────────
NUM_DAYS = 730          # 2 years
START_DATE = date(2023, 1, 1)

# ── Shops ────────────────────────────────────────────────────────────────────
SHOPS = [
    {'shop_id': 'S001', 'shop_name': 'Pune Footwear - Main',      'shop_location': 'Pune', 'multiplier': 1.5},
    {'shop_id': 'S002', 'shop_name': 'Pune Footwear - Wakad',     'shop_location': 'Pune', 'multiplier': 1.3},
    {'shop_id': 'S003', 'shop_name': 'Pune Footwear - Hinjewadi', 'shop_location': 'Pune', 'multiplier': 1.1},
    {'shop_id': 'S004', 'shop_name': 'Pune Footwear - Pimpri',    'shop_location': 'Pune', 'multiplier': 1.0},
    {'shop_id': 'S005', 'shop_name': 'Pune Footwear - Camp',      'shop_location': 'Pune', 'multiplier': 0.9},
    {'shop_id': 'S006', 'shop_name': 'Pune Footwear - Kothrud',   'shop_location': 'Pune', 'multiplier': 0.85},
    {'shop_id': 'S007', 'shop_name': 'Pune Footwear - Hadapsar',  'shop_location': 'Pune', 'multiplier': 0.8},
    {'shop_id': 'S008', 'shop_name': 'Pune Footwear - Baner',     'shop_location': 'Pune', 'multiplier': 1.2},
    {'shop_id': 'S009', 'shop_name': 'Pune Footwear - Viman',     'shop_location': 'Pune', 'multiplier': 0.75},
    {'shop_id': 'S010', 'shop_name': 'Pune Footwear - Katraj',    'shop_location': 'Pune', 'multiplier': 0.7},
]

# ── Suppliers ────────────────────────────────────────────────────────────────
SUPPLIERS = [
    {'supplier_id': 'SUP001', 'supplier_name': 'ABC Footwear Suppliers',   'lead_time_days': 5},
    {'supplier_id': 'SUP002', 'supplier_name': 'Metro Shoe Distributors',  'lead_time_days': 7},
    {'supplier_id': 'SUP003', 'supplier_name': 'Pune Footwear Wholesale',  'lead_time_days': 10},
    {'supplier_id': 'SUP004', 'supplier_name': 'National Shoe Traders',    'lead_time_days': 6},
    {'supplier_id': 'SUP005', 'supplier_name': 'FastTrack Footwear Co.',   'lead_time_days': 4},
]

# ── Products ─────────────────────────────────────────────────────────────────
PRODUCTS = [
    # (product_id, name, category, subcategory, brand, gender, size, color, material, unit_price, cost_price, base_demand, seasonal_peak, supplier_idx, speed)
    ('P001', 'Nike Air Running Shoes',    'Sports',  'Running',  'Nike',     'Men',   '8',  'Black',  'Mesh',    2999, 1800, 8,  'Summer',        0, 'fast'),
    ('P002', 'Adidas Ultraboost',         'Sports',  'Running',  'Adidas',   'Men',   '9',  'White',  'Knit',    3499, 2100, 7,  'Summer',        1, 'fast'),
    ('P003', 'Puma Sports Shoes',         'Sports',  'Training', 'Puma',     'Men',   '8',  'Blue',   'Mesh',    1999, 1200, 6,  'Summer',        2, 'medium'),
    ('P004', 'Campus Running Shoes',      'Sports',  'Running',  'Campus',   'Men',   '7',  'Red',    'Mesh',    999,  600,  9,  'Summer',        3, 'fast'),
    ('P005', 'Skechers Go Walk',          'Casual',  'Walking',  'Skechers', 'Men',   '9',  'Grey',   'Knit',    2499, 1500, 5,  'Festival',      0, 'medium'),
    ('P006', 'Bata Formal Shoes',         'Formal',  'Oxford',   'Bata',     'Men',   '8',  'Black',  'Leather', 1799, 1000, 4,  'Festival',      1, 'medium'),
    ('P007', 'Red Tape Formal Shoes',     'Formal',  'Derby',    'RedTape',  'Men',   '9',  'Brown',  'Leather', 2299, 1400, 3,  'Festival',      2, 'slow'),
    ('P008', 'Woodland Boots',            'Casual',  'Boots',    'Woodland', 'Men',   '9',  'Brown',  'Leather', 3299, 2000, 3,  'Winter',        3, 'slow'),
    ('P009', 'Sparx Casual Shoes',        'Casual',  'Sneakers', 'Sparx',    'Men',   '8',  'White',  'Synthetic',799, 450,  10, 'Festival',      4, 'fast'),
    ('P010', 'Liberty Loafers',           'Casual',  'Loafers',  'Liberty',  'Men',   '8',  'Black',  'Leather', 1299, 750,  5,  'Festival',      0, 'medium'),
    ('P011', 'Nike Women Running',        'Sports',  'Running',  'Nike',     'Women', '6',  'Pink',   'Mesh',    2799, 1700, 7,  'Summer',        1, 'fast'),
    ('P012', 'Adidas Women Sneakers',     'Sports',  'Training', 'Adidas',   'Women', '5',  'White',  'Knit',    2999, 1800, 6,  'Summer',        2, 'fast'),
    ('P013', 'Bata Ladies Sandals',       'Sandals', 'Flat',     'Bata',     'Women', '5',  'Gold',   'Synthetic',699, 380,  8,  'Summer',        3, 'fast'),
    ('P014', 'Liberty Ladies Heels',      'Formal',  'Heels',    'Liberty',  'Women', '5',  'Black',  'Leather', 1499, 850,  4,  'Festival',      4, 'medium'),
    ('P015', 'Skechers Women Casual',     'Casual',  'Walking',  'Skechers', 'Women', '6',  'Purple', 'Knit',    2199, 1300, 5,  'Festival',      0, 'medium'),
    ('P016', 'Puma Women Sandals',        'Sandals', 'Sport',    'Puma',     'Women', '5',  'White',  'Rubber',  1299, 750,  6,  'Summer',        1, 'medium'),
    ('P017', 'Campus Ladies Shoes',       'Casual',  'Sneakers', 'Campus',   'Women', '4',  'Red',    'Mesh',    899,  500,  7,  'Festival',      2, 'fast'),
    ('P018', 'Woodland Ladies Boots',     'Casual',  'Boots',    'Woodland', 'Women', '5',  'Brown',  'Leather', 2999, 1800, 2,  'Winter',        3, 'slow'),
    ('P019', 'Bata School Shoes',         'Kids',    'School',   'Bata',     'Kids',  '3',  'Black',  'Leather', 699,  380,  10, 'School Season', 4, 'fast'),
    ('P020', 'Liberty Kids Shoes',        'Kids',    'School',   'Liberty',  'Kids',  '2',  'Black',  'Synthetic',599, 320,  9,  'School Season', 0, 'fast'),
    ('P021', 'Nike Kids Sneakers',        'Kids',    'Casual',   'Nike',     'Kids',  '3',  'Blue',   'Mesh',    1499, 900,  6,  'Festival',      1, 'medium'),
    ('P022', 'Adidas Kids Sports',        'Sports',  'Training', 'Adidas',   'Kids',  '2',  'Green',  'Mesh',    1299, 780,  5,  'Summer',        2, 'medium'),
    ('P023', 'Campus Kids Shoes',         'Kids',    'Casual',   'Campus',   'Kids',  '3',  'Red',    'Mesh',    699,  380,  8,  'Festival',      3, 'fast'),
    ('P024', 'Sparx Slippers',            'Slippers','Flip-Flop','Sparx',    'Men',   '8',  'Blue',   'Rubber',  299,  150,  12, 'Summer',        4, 'fast'),
    ('P025', 'Bata Slippers',             'Slippers','Flip-Flop','Bata',     'Men',   '9',  'Brown',  'Rubber',  249,  120,  11, 'Summer',        0, 'fast'),
    ('P026', 'Puma Slippers',             'Slippers','Slide',    'Puma',     'Men',   '8',  'Black',  'Rubber',  599,  320,  8,  'Summer',        1, 'fast'),
    ('P027', 'Ladies Flat Sandals',       'Sandals', 'Flat',     'Liberty',  'Women', '5',  'Silver', 'Synthetic',499, 260,  9,  'Summer',        2, 'fast'),
    ('P028', 'Woodland Trekking Shoes',   'Sports',  'Trekking', 'Woodland', 'Men',   '9',  'Khaki',  'Leather', 3999, 2400, 2,  'Winter',        3, 'slow'),
    ('P029', 'Skechers Memory Foam',      'Casual',  'Walking',  'Skechers', 'Women', '6',  'Beige',  'Knit',    2699, 1600, 4,  'Festival',      4, 'medium'),
    ('P030', 'RedTape Sneakers',          'Casual',  'Sneakers', 'RedTape',  'Men',   '9',  'White',  'Leather', 1999, 1200, 5,  'Festival',      0, 'medium'),
    ('P031', 'Nike Formal Shoes',         'Formal',  'Oxford',   'Nike',     'Men',   '8',  'Black',  'Leather', 3499, 2100, 3,  'Festival',      1, 'slow'),
    ('P032', 'Adidas Sandals',            'Sandals', 'Sport',    'Adidas',   'Men',   '9',  'Black',  'Rubber',  1499, 850,  6,  'Summer',        2, 'medium'),
    ('P033', 'Bata Casual Shoes',         'Casual',  'Loafers',  'Bata',     'Men',   '8',  'Brown',  'Leather', 1199, 680,  6,  'Festival',      3, 'medium'),
    ('P034', 'Campus Sports Shoes',       'Sports',  'Training', 'Campus',   'Men',   '8',  'Orange', 'Mesh',    1099, 620,  7,  'Summer',        4, 'fast'),
    ('P035', 'Sparx Women Sandals',       'Sandals', 'Flat',     'Sparx',    'Women', '5',  'Pink',   'Rubber',  399,  200,  8,  'Summer',        0, 'fast'),
    ('P036', 'Liberty Formal Shoes',      'Formal',  'Oxford',   'Liberty',  'Men',   '8',  'Black',  'Leather', 1599, 900,  4,  'Festival',      1, 'medium'),
    ('P037', 'Puma Kids Shoes',           'Kids',    'Casual',   'Puma',     'Kids',  '2',  'Yellow', 'Mesh',    999,  560,  5,  'Festival',      2, 'medium'),
    ('P038', 'Woodland Casual Shoes',     'Casual',  'Lace-up',  'Woodland', 'Men',   '9',  'Olive',  'Leather', 2499, 1500, 4,  'Winter',        3, 'medium'),
    ('P039', 'Skechers Kids Shoes',       'Kids',    'School',   'Skechers', 'Kids',  '3',  'Blue',   'Mesh',    1199, 680,  6,  'School Season', 4, 'fast'),
    ('P040', 'RedTape Boots',             'Casual',  'Boots',    'RedTape',  'Men',   '9',  'Black',  'Leather', 2799, 1700, 2,  'Winter',        0, 'slow'),
]

# ── Holidays ─────────────────────────────────────────────────────────────────
HOLIDAYS = {}
for yr in [2023, 2024]:
    HOLIDAYS.update({
        date(yr, 1, 26): 'Republic Day',
        date(yr, 3, 8):  'Holi',
        date(yr, 4, 14): 'Ambedkar Jayanti',
        date(yr, 8, 15): 'Independence Day',
        date(yr, 10, 2): 'Gandhi Jayanti',
        date(yr, 12, 25): 'Christmas',
    })
# Festival windows (multi-day)
FESTIVAL_WINDOWS = [
    (date(2023, 10, 20), date(2023, 10, 24), 'Dussehra'),
    (date(2023, 11, 10), date(2023, 11, 14), 'Diwali'),
    (date(2023, 3, 7),   date(2023, 3, 9),   'Holi'),
    (date(2023, 4, 21),  date(2023, 4, 23),  'Eid'),
    (date(2024, 10, 8),  date(2024, 10, 12), 'Dussehra'),
    (date(2024, 10, 29), date(2024, 11, 2),  'Diwali'),
    (date(2024, 3, 25),  date(2024, 3, 27),  'Holi'),
    (date(2024, 4, 10),  date(2024, 4, 12),  'Eid'),
    (date(2023, 6, 1),   date(2023, 6, 15),  'School Season'),
    (date(2024, 6, 1),   date(2024, 6, 15),  'School Season'),
]

def get_holiday(d):
    if d in HOLIDAYS:
        return True, HOLIDAYS[d]
    for start, end, name in FESTIVAL_WINDOWS:
        if start <= d <= end:
            return True, name
    return False, ''

def get_season(d):
    m = d.month
    if m in (12, 1, 2):    return 'Winter'
    if m in (3, 4, 5):     return 'Summer'
    if m in (6, 7, 8, 9):  return 'Monsoon'
    if m in (10, 11):      return 'Festival'
    return 'Summer'

def seasonal_multiplier(season, product_peak):
    if season == product_peak:
        return 1.6
    adjacent = {
        'Summer':        ['Monsoon', 'Festival'],
        'Monsoon':       ['Summer', 'Festival'],
        'Winter':        ['Festival', 'Monsoon'],
        'Festival':      ['Summer', 'Winter'],
        'School Season': ['Summer', 'Festival'],
    }
    if season in adjacent.get(product_peak, []):
        return 1.2
    return 0.8

def promotion_for_day(d, is_holiday, holiday_name, is_weekend):
    if is_holiday and holiday_name in ('Diwali', 'Dussehra', 'Holi', 'Eid'):
        return True, 'Festival Sale', random.uniform(15, 25)
    if is_weekend and random.random() < 0.3:
        return True, 'Weekend Sale', random.uniform(5, 15)
    if d.month in (1, 7) and random.random() < 0.15:
        return True, 'Season End Sale', random.uniform(20, 30)
    if random.random() < 0.05:
        return True, 'Clearance Sale', random.uniform(10, 20)
    return False, 'No Promotion', 0.0

def demand_qty(base, shop_mult, season_mult, is_weekend, is_holiday, promo, promo_disc, speed):
    qty = base * shop_mult * season_mult
    if is_weekend:
        qty *= 1.25
    if is_holiday:
        qty *= 1.4
    if promo:
        qty *= (1 + promo_disc / 100 * 0.8)
    speed_mult = {'fast': 1.2, 'medium': 1.0, 'slow': 0.7}[speed]
    qty *= speed_mult
    noise = random.gauss(1.0, 0.15)
    qty = max(1, round(qty * noise))
    return qty


def main():
    rows = []
    sale_id = 1

    for shop in SHOPS:
        for prod in PRODUCTS:
            (pid, pname, cat, subcat, brand, gender, size, color, material,
             unit_price, cost_price, base_demand, peak_season, sup_idx, speed) = prod
            supplier = SUPPLIERS[sup_idx]

            for day_offset in range(NUM_DAYS):
                d = START_DATE + timedelta(days=day_offset)
                season = get_season(d)
                is_holiday, holiday_name = get_holiday(d)
                is_weekend = d.weekday() >= 5
                day_of_week = d.weekday()
                month = d.month
                week_number = d.isocalendar()[1]

                promo, promo_type, promo_disc = promotion_for_day(d, is_holiday, holiday_name, is_weekend)
                s_mult = seasonal_multiplier(season, peak_season)
                qty = demand_qty(base_demand, shop['multiplier'], s_mult,
                                 is_weekend, is_holiday, promo, promo_disc, speed)

                # Pricing with small random variation
                up = round(unit_price * random.uniform(0.97, 1.03), 2)
                cp = round(cost_price * random.uniform(0.97, 1.03), 2)
                disc_pct = round(promo_disc, 2)
                gross = round(qty * up, 2)
                disc_amt = round(gross * disc_pct / 100, 2)
                total_sales = round(gross - disc_amt, 2)
                profit = round(total_sales - qty * cp, 2)

                rows.append({
                    'sale_id':          f'SAL{sale_id:07d}',
                    'shop_id':          shop['shop_id'],
                    'shop_name':        shop['shop_name'],
                    'shop_location':    shop['shop_location'],
                    'product_id':       pid,
                    'product_name':     pname,
                    'category':         cat,
                    'subcategory':      subcat,
                    'brand':            brand,
                    'gender':           gender,
                    'size':             size,
                    'color':            color,
                    'material':         material,
                    'supplier_id':      supplier['supplier_id'],
                    'supplier_name':    supplier['supplier_name'],
                    'lead_time_days':   supplier['lead_time_days'],
                    'date':             d.strftime('%Y-%m-%d'),
                    'quantity':         qty,
                    'unit_price':       up,
                    'cost_price':       cp,
                    'discount_percent': disc_pct,
                    'discount_amount':  disc_amt,
                    'total_sales':      total_sales,
                    'profit':           profit,
                    'promotion':        1 if promo else 0,
                    'promotion_type':   promo_type,
                    'promotion_discount': round(promo_disc, 2),
                    'is_holiday':       1 if is_holiday else 0,
                    'holiday_name':     holiday_name,
                    'season':           season,
                    'day_of_week':      day_of_week,
                    'day_name':         d.strftime('%A'),
                    'week_number':      week_number,
                    'month':            month,
                    'month_name':       d.strftime('%B'),
                    'quarter':          (month - 1) // 3 + 1,
                    'year':             d.year,
                    'is_weekend':       1 if is_weekend else 0,
                })
                sale_id += 1

    fieldnames = list(rows[0].keys())
    output_file = 'footwear_sales_dataset.csv'
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows):,} records → {output_file}")
    print(f"Shops: {len(SHOPS)}, Products: {len(PRODUCTS)}, Days: {NUM_DAYS}")


if __name__ == '__main__':
    main()
