"""
generate_thakur_footwear.py
Generates ~5,00,000 transaction-level sales records for Thakur Footwear.
Date range : 01-Jan-2025 to 31-Dec-2025
Output     : thakur_footwear_sales_500k.csv
             thakur_footwear_sample.csv  (~1000 rows)

Usage: python generate_thakur_footwear.py
"""

import csv
import math
import random
from datetime import date, timedelta

random.seed(2025)

# ── Constants ────────────────────────────────────────────────────────────────
START_DATE  = date(2025, 1, 1)
END_DATE    = date(2025, 12, 31)
NUM_DAYS    = (END_DATE - START_DATE).days + 1   # 365
TARGET_ROWS = 500_000
OUTPUT_FULL = "thakur_footwear_sales_500k.csv"
OUTPUT_SAMPLE = "thakur_footwear_sample.csv"

# ── Shop ─────────────────────────────────────────────────────────────────────
SHOP = {
    "shop_id":       "TF001",
    "shop_name":     "Thakur Footwear",
    "shop_location": "Mumbai",
}

# ── Suppliers ────────────────────────────────────────────────────────────────
SUPPLIERS = [
    {"supplier_id": "SUP01", "supplier_name": "Raj Footwear Distributors",  "lead_time_days": 5},
    {"supplier_id": "SUP02", "supplier_name": "Mumbai Shoe Wholesale Co.",   "lead_time_days": 7},
    {"supplier_id": "SUP03", "supplier_name": "National Footwear Traders",   "lead_time_days": 10},
    {"supplier_id": "SUP04", "supplier_name": "FastStep Supply Chain",       "lead_time_days": 4},
    {"supplier_id": "SUP05", "supplier_name": "Thakur Preferred Suppliers",  "lead_time_days": 6},
]

# ── Products ─────────────────────────────────────────────────────────────────
# Fields: product_id, product_name, category, subcategory, brand,
#         gender, size, color, material, unit_price, cost_price,
#         base_txn_per_day, peak_season, supplier_idx, speed
# base_txn_per_day = average number of transactions per day for this product
# speed            = fast / medium / slow  (affects demand multiplier)

PRODUCTS = [
    # ── Running Shoes ────────────────────────────────────────────────────────
    ("TFP001","Nike Air Max Running Shoes",    "Running Shoes","Running",  "Nike",    "Men",   "8",  "Black",  "Mesh",    3499,2100,4.2,"Summer",   0,"fast"),
    ("TFP002","Adidas Ultraboost Running",     "Running Shoes","Running",  "Adidas",  "Men",   "9",  "White",  "Knit",    3999,2400,3.8,"Summer",   1,"fast"),
    ("TFP003","Puma Velocity Running Shoes",   "Running Shoes","Running",  "Puma",    "Men",   "8",  "Blue",   "Mesh",    2499,1500,3.5,"Summer",   2,"fast"),
    ("TFP004","Campus Running Pro",            "Running Shoes","Running",  "Campus",  "Men",   "7",  "Red",    "Mesh",    1199, 700,5.0,"Summer",   3,"fast"),
    ("TFP005","Nike Women Air Running",        "Running Shoes","Running",  "Nike",    "Women", "5",  "Pink",   "Mesh",    3299,1980,3.2,"Summer",   4,"fast"),
    ("TFP006","Adidas Women Running Boost",    "Running Shoes","Running",  "Adidas",  "Women", "6",  "Purple", "Knit",    3599,2160,2.8,"Summer",   0,"fast"),

    # ── Sports Shoes ─────────────────────────────────────────────────────────
    ("TFP007","Nike Court Sports Shoes",       "Sports Shoes", "Training", "Nike",    "Men",   "9",  "White",  "Synthetic",2999,1800,3.5,"Summer",  1,"fast"),
    ("TFP008","Adidas Predator Sports",        "Sports Shoes", "Football", "Adidas",  "Men",   "8",  "Black",  "Synthetic",2799,1680,3.0,"Summer",  2,"fast"),
    ("TFP009","Puma Future Sports Shoes",      "Sports Shoes", "Training", "Puma",    "Men",   "9",  "Yellow", "Mesh",    2299,1380,3.2,"Summer",   3,"medium"),
    ("TFP010","Campus Sports Pro",             "Sports Shoes", "Training", "Campus",  "Men",   "8",  "Orange", "Mesh",    1099, 660,4.5,"Summer",   4,"fast"),
    ("TFP011","Skechers Sport Shoes",          "Sports Shoes", "Training", "Skechers","Men",   "9",  "Grey",   "Mesh",    2199,1320,2.8,"Summer",   0,"medium"),

    # ── Sneakers ─────────────────────────────────────────────────────────────
    ("TFP012","Nike Air Force Sneakers",       "Sneakers",     "Lifestyle","Nike",    "Men",   "9",  "White",  "Leather", 4499,2700,3.0,"Festival", 1,"fast"),
    ("TFP013","Adidas Stan Smith Sneakers",    "Sneakers",     "Lifestyle","Adidas",  "Men",   "8",  "White",  "Leather", 3999,2400,2.8,"Festival", 2,"fast"),
    ("TFP014","Puma Suede Sneakers",           "Sneakers",     "Lifestyle","Puma",    "Men",   "9",  "Black",  "Suede",   2999,1800,2.5,"Festival", 3,"medium"),
    ("TFP015","Sparx Sneakers",                "Sneakers",     "Casual",   "Sparx",   "Men",   "8",  "White",  "Synthetic",899, 500,5.5,"Festival", 4,"fast"),
    ("TFP016","RedTape Sneakers",              "Sneakers",     "Casual",   "RedTape", "Men",   "9",  "White",  "Leather", 1999,1200,3.0,"Festival", 0,"medium"),
    ("TFP017","Nike Women Sneakers",           "Sneakers",     "Lifestyle","Nike",    "Women", "5",  "Pink",   "Leather", 3999,2400,2.5,"Festival", 1,"fast"),
    ("TFP018","Adidas Women Originals",        "Sneakers",     "Lifestyle","Adidas",  "Women", "6",  "White",  "Leather", 3499,2100,2.2,"Festival", 2,"fast"),

    # ── Formal Shoes ─────────────────────────────────────────────────────────
    ("TFP019","Bata Oxford Formal Shoes",      "Formal Shoes", "Oxford",   "Bata",    "Men",   "8",  "Black",  "Leather", 1799,1000,2.5,"Festival", 3,"medium"),
    ("TFP020","Red Tape Derby Formal",         "Formal Shoes", "Derby",    "RedTape", "Men",   "9",  "Brown",  "Leather", 2499,1500,2.0,"Festival", 4,"medium"),
    ("TFP021","Liberty Formal Oxford",         "Formal Shoes", "Oxford",   "Liberty", "Men",   "8",  "Black",  "Leather", 1599, 900,2.2,"Festival", 0,"medium"),
    ("TFP022","Woodland Formal Shoes",         "Formal Shoes", "Derby",    "Woodland","Men",   "9",  "Brown",  "Leather", 2999,1800,1.5,"Festival", 1,"slow"),
    ("TFP023","Bata Ladies Formal Heels",      "Formal Shoes", "Heels",    "Bata",    "Women", "5",  "Black",  "Leather", 1499, 850,2.0,"Festival", 2,"medium"),
    ("TFP024","Liberty Ladies Formal",         "Formal Shoes", "Heels",    "Liberty", "Women", "5",  "Nude",   "Leather", 1699, 950,1.8,"Festival", 3,"medium"),

    # ── Casual Shoes ─────────────────────────────────────────────────────────
    ("TFP025","Skechers Go Walk Casual",       "Casual Shoes", "Walking",  "Skechers","Men",   "9",  "Grey",   "Knit",    2699,1620,3.0,"Festival", 4,"medium"),
    ("TFP026","Bata Casual Lace-up",           "Casual Shoes", "Lace-up",  "Bata",    "Men",   "8",  "Brown",  "Leather", 1299, 750,3.5,"Festival", 0,"medium"),
    ("TFP027","Sparx Casual Shoes",            "Casual Shoes", "Sneakers", "Sparx",   "Men",   "8",  "White",  "Synthetic",799, 450,5.0,"Festival", 1,"fast"),
    ("TFP028","Woodland Casual Lace-up",       "Casual Shoes", "Lace-up",  "Woodland","Men",   "9",  "Olive",  "Leather", 2499,1500,2.0,"Winter",   2,"medium"),
    ("TFP029","Skechers Women Casual",         "Casual Shoes", "Walking",  "Skechers","Women", "6",  "Beige",  "Knit",    2499,1500,2.5,"Festival", 3,"medium"),
    ("TFP030","Campus Casual Shoes",           "Casual Shoes", "Sneakers", "Campus",  "Women", "5",  "Red",    "Mesh",     999, 580,3.8,"Festival", 4,"fast"),

    # ── School Shoes ─────────────────────────────────────────────────────────
    ("TFP031","Bata School Shoes Boys",        "School Shoes", "School",   "Bata",    "Kids",  "3",  "Black",  "Leather",  699, 380,6.0,"School",   0,"fast"),
    ("TFP032","Liberty School Shoes Boys",     "School Shoes", "School",   "Liberty", "Kids",  "2",  "Black",  "Synthetic",599, 320,5.5,"School",   1,"fast"),
    ("TFP033","Bata School Shoes Girls",       "School Shoes", "School",   "Bata",    "Kids",  "3",  "Black",  "Leather",  699, 380,5.0,"School",   2,"fast"),
    ("TFP034","Liberty School Shoes Girls",    "School Shoes", "School",   "Liberty", "Kids",  "2",  "Black",  "Synthetic",599, 320,4.5,"School",   3,"fast"),
    ("TFP035","Skechers School Shoes",         "School Shoes", "School",   "Skechers","Kids",  "3",  "Black",  "Mesh",    1199, 680,3.5,"School",   4,"fast"),

    # ── Walking Shoes ────────────────────────────────────────────────────────
    ("TFP036","Skechers Go Walk Men",          "Walking Shoes","Walking",  "Skechers","Men",   "9",  "Black",  "Knit",    2499,1500,3.0,"Summer",   0,"medium"),
    ("TFP037","Bata Comfit Walking",           "Walking Shoes","Walking",  "Bata",    "Men",   "8",  "Brown",  "Leather", 1499, 850,2.8,"Summer",   1,"medium"),
    ("TFP038","Liberty Walker",                "Walking Shoes","Walking",  "Liberty", "Men",   "8",  "Black",  "Leather", 1299, 740,2.5,"Summer",   2,"medium"),
    ("TFP039","Skechers Women Walk",           "Walking Shoes","Walking",  "Skechers","Women", "5",  "White",  "Knit",    2299,1380,2.8,"Summer",   3,"medium"),

    # ── Loafers ──────────────────────────────────────────────────────────────
    ("TFP040","Liberty Loafers Men",           "Loafers",      "Loafers",  "Liberty", "Men",   "8",  "Black",  "Leather", 1299, 750,2.5,"Festival", 4,"medium"),
    ("TFP041","Bata Loafers Men",              "Loafers",      "Loafers",  "Bata",    "Men",   "9",  "Brown",  "Leather", 1199, 680,2.2,"Festival", 0,"medium"),
    ("TFP042","RedTape Loafers",               "Loafers",      "Loafers",  "RedTape", "Men",   "9",  "Black",  "Leather", 1799,1080,1.8,"Festival", 1,"slow"),

    # ── Sandals ──────────────────────────────────────────────────────────────
    ("TFP043","Bata Ladies Sandals Flat",      "Sandals",      "Flat",     "Bata",    "Women", "5",  "Gold",   "Synthetic",699, 380,5.5,"Summer",   2,"fast"),
    ("TFP044","Liberty Ladies Sandals",        "Sandals",      "Flat",     "Liberty", "Women", "5",  "Silver", "Synthetic",599, 320,5.0,"Summer",   3,"fast"),
    ("TFP045","Sparx Women Sandals",           "Sandals",      "Flat",     "Sparx",   "Women", "5",  "Pink",   "Rubber",   399, 200,6.0,"Summer",   4,"fast"),
    ("TFP046","Adidas Adilette Sandals",       "Sandals",      "Sport",    "Adidas",  "Men",   "9",  "Black",  "Rubber",  1499, 850,3.5,"Summer",   0,"medium"),
    ("TFP047","Puma Leadcat Sandals",          "Sandals",      "Sport",    "Puma",    "Men",   "8",  "White",  "Rubber",  1299, 750,3.2,"Summer",   1,"medium"),

    # ── Slippers ─────────────────────────────────────────────────────────────
    ("TFP048","Sparx Flip Flops Men",          "Slippers",     "Flip-Flop","Sparx",   "Men",   "8",  "Blue",   "Rubber",   299, 150,8.0,"Summer",   2,"fast"),
    ("TFP049","Bata Slippers Men",             "Slippers",     "Flip-Flop","Bata",    "Men",   "9",  "Brown",  "Rubber",   249, 120,7.5,"Summer",   3,"fast"),
    ("TFP050","Puma Slide Slippers",           "Slippers",     "Slide",    "Puma",    "Men",   "8",  "Black",  "Rubber",   699, 380,5.0,"Summer",   4,"fast"),
    ("TFP051","Bata Ladies Slippers",          "Slippers",     "Flip-Flop","Bata",    "Women", "5",  "Pink",   "Rubber",   199, 100,7.0,"Summer",   0,"fast"),
    ("TFP052","Liberty Ladies Slippers",       "Slippers",     "Flat",     "Liberty", "Women", "5",  "Gold",   "Rubber",   299, 150,6.0,"Summer",   1,"fast"),

    # ── Boots ────────────────────────────────────────────────────────────────
    ("TFP053","Woodland Trekking Boots",       "Boots",        "Trekking", "Woodland","Men",   "9",  "Brown",  "Leather", 3999,2400,1.5,"Winter",   2,"slow"),
    ("TFP054","RedTape Ankle Boots",           "Boots",        "Ankle",    "RedTape", "Men",   "9",  "Black",  "Leather", 2999,1800,1.8,"Winter",   3,"slow"),
    ("TFP055","Bata Rain Boots",               "Boots",        "Rain",     "Bata",    "Men",   "8",  "Black",  "Rubber",  1299, 750,2.5,"Monsoon",  4,"medium"),
    ("TFP056","Woodland Ladies Boots",         "Boots",        "Ankle",    "Woodland","Women", "5",  "Brown",  "Leather", 2999,1800,1.2,"Winter",   0,"slow"),

    # ── Ladies Sandals (premium) ─────────────────────────────────────────────
    ("TFP057","Bata Wedge Sandals",            "Ladies Sandals","Wedge",   "Bata",    "Women", "5",  "Tan",    "Synthetic",999, 560,3.5,"Summer",   1,"medium"),
    ("TFP058","Liberty Block Heel Sandals",    "Ladies Sandals","Block",   "Liberty", "Women", "5",  "Black",  "Leather", 1299, 740,2.8,"Summer",   2,"medium"),
    ("TFP059","Catwalk Heeled Sandals",        "Ladies Sandals","Heels",   "Catwalk", "Women", "5",  "Gold",   "Synthetic",1799,1000,2.0,"Festival", 3,"medium"),
    ("TFP060","Metro Ladies Sandals",          "Ladies Sandals","Flat",    "Metro",   "Women", "5",  "Silver", "Leather", 1499, 850,2.5,"Summer",   4,"medium"),

    # ── Kids Shoes ───────────────────────────────────────────────────────────
    ("TFP061","Nike Kids Sneakers",            "Kids Shoes",   "Casual",   "Nike",    "Kids",  "3",  "Blue",   "Mesh",    1499, 900,3.0,"Festival", 0,"medium"),
    ("TFP062","Adidas Kids Sports",            "Kids Shoes",   "Sports",   "Adidas",  "Kids",  "2",  "Green",  "Mesh",    1299, 780,2.8,"Summer",   1,"medium"),
    ("TFP063","Puma Kids Shoes",               "Kids Shoes",   "Casual",   "Puma",    "Kids",  "2",  "Yellow", "Mesh",     999, 560,3.2,"Festival", 2,"medium"),
    ("TFP064","Campus Kids Shoes",             "Kids Shoes",   "Casual",   "Campus",  "Kids",  "3",  "Red",    "Mesh",     699, 380,4.5,"Festival", 3,"fast"),
    ("TFP065","Bata Kids Casual Shoes",        "Kids Shoes",   "Casual",   "Bata",    "Kids",  "3",  "White",  "Synthetic",599, 320,4.0,"Festival", 4,"fast"),
]


# ── 2025 Indian Holidays & Festival Windows ──────────────────────────────────
HOLIDAYS_2025 = {
    date(2025, 1, 26):  "Republic Day",
    date(2025, 3, 14):  "Holi",
    date(2025, 4, 14):  "Ambedkar Jayanti",
    date(2025, 4, 18):  "Good Friday",
    date(2025, 8, 15):  "Independence Day",
    date(2025, 8, 27):  "Janmashtami",
    date(2025, 10, 2):  "Gandhi Jayanti",
    date(2025, 10, 20): "Dussehra",
    date(2025, 10, 20): "Dussehra",
    date(2025, 11, 5):  "Diwali",
    date(2025, 11, 6):  "Diwali",
    date(2025, 12, 25): "Christmas",
}

# Multi-day festival windows  (start, end, name, demand_boost)
FESTIVAL_WINDOWS = [
    (date(2025, 1, 24), date(2025, 1, 27), "Republic Day",    1.30),
    (date(2025, 3, 12), date(2025, 3, 16), "Holi",            1.50),
    (date(2025, 3, 30), date(2025, 4, 2),  "Eid",             1.55),
    (date(2025, 6, 1),  date(2025, 6, 20), "School Season",   1.80),  # school shoe spike
    (date(2025, 7, 1),  date(2025, 7, 7),  "Monsoon Sale",    1.25),
    (date(2025, 10, 1), date(2025, 10, 5), "Navratri",        1.40),
    (date(2025, 10, 17),date(2025, 10, 22),"Dussehra",        1.60),
    (date(2025, 10, 28),date(2025, 11, 8), "Diwali",          1.80),
    (date(2025, 12, 20),date(2025, 12, 31),"Christmas/NYE",   1.45),
    (date(2025, 1, 1),  date(2025, 1, 3),  "New Year",        1.35),
]

# Back-to-school window (Jan re-opening)
SCHOOL_WINDOWS = [
    (date(2025, 1, 6),  date(2025, 1, 20)),   # Jan school re-open
    (date(2025, 6, 1),  date(2025, 6, 20)),   # June new academic year
]


def get_festival(d):
    """Return (is_holiday, holiday_name, festival_boost)."""
    for start, end, name, boost in FESTIVAL_WINDOWS:
        if start <= d <= end:
            return True, name, boost
    if d in HOLIDAYS_2025:
        return True, HOLIDAYS_2025[d], 1.30
    return False, "", 1.0


def get_season(d):
    m = d.month
    if m in (12, 1, 2):   return "Winter"
    if m in (3, 4, 5):    return "Summer"
    if m in (6, 7, 8, 9): return "Monsoon"
    return "Festival"          # Oct, Nov


def seasonal_mult(season, peak):
    """How well does this product's peak match today's season."""
    if peak == "School":
        # handled separately via school windows
        return 1.0
    table = {
        ("Summer",   "Summer"):   1.70,
        ("Summer",   "Monsoon"):  0.75,
        ("Summer",   "Winter"):   0.65,
        ("Summer",   "Festival"): 0.90,
        ("Monsoon",  "Summer"):   0.80,
        ("Monsoon",  "Monsoon"):  1.50,
        ("Monsoon",  "Winter"):   0.85,
        ("Monsoon",  "Festival"): 0.90,
        ("Winter",   "Summer"):   0.70,
        ("Winter",   "Monsoon"):  0.80,
        ("Winter",   "Winter"):   1.60,
        ("Winter",   "Festival"): 0.95,
        ("Festival", "Summer"):   1.10,
        ("Festival", "Monsoon"):  0.85,
        ("Festival", "Winter"):   1.10,
        ("Festival", "Festival"): 1.65,
    }
    return table.get((season, peak), 1.0)


def school_mult(d, peak):
    """Extra multiplier for school shoes during school windows."""
    if peak != "School":
        return 1.0
    for start, end in SCHOOL_WINDOWS:
        if start <= d <= end:
            return 2.5
    return 0.4   # very slow outside school season


def promotion_for_day(d, is_holiday, holiday_name, is_weekend):
    """Return (promotion bool, promotion_type str, discount_pct float)."""
    if is_holiday and holiday_name in ("Diwali", "Dussehra", "Holi", "Eid",
                                        "Navratri", "Christmas/NYE"):
        return True, "Festival Sale", round(random.uniform(15, 30), 2)
    if is_holiday and holiday_name in ("Republic Day", "Independence Day",
                                        "School Season", "New Year"):
        return True, "Special Sale", round(random.uniform(10, 20), 2)
    if is_weekend and random.random() < 0.35:
        return True, "Weekend Sale", round(random.uniform(5, 15), 2)
    if d.month in (1, 7) and random.random() < 0.18:
        return True, "Season End Sale", round(random.uniform(20, 35), 2)
    if random.random() < 0.04:
        return True, "Clearance Sale", round(random.uniform(10, 25), 2)
    if random.random() < 0.03:
        return True, "Buy 1 Get 1", round(random.uniform(40, 50), 2)
    return False, "No Promotion", 0.0


# ── Transaction-count engine ─────────────────────────────────────────────────

SPEED_MULT = {"fast": 1.30, "medium": 1.00, "slow": 0.60}

def txn_count_for_day(base_txn, peak, speed, season, is_weekend,
                       festival_boost, promo, promo_disc, d):
    """
    Return the number of individual transactions to generate for this
    product on this day.  Each transaction will have its own random qty.
    """
    m = base_txn
    m *= SPEED_MULT[speed]
    m *= seasonal_mult(season, peak)
    m *= school_mult(d, peak)
    m *= festival_boost
    if is_weekend:
        m *= 1.30
    if promo:
        m *= (1.0 + promo_disc / 100 * 0.6)
    # occasional high-sales day
    if random.random() < 0.03:
        m *= random.uniform(1.8, 2.5)
    # gaussian noise
    m = max(0.0, random.gauss(m, m * 0.20))
    # convert to integer transaction count (at least 0)
    count = max(0, round(m))
    return count


def qty_per_txn(speed, promo, promo_disc):
    """Units sold in a single transaction."""
    base = {"fast": 2, "medium": 2, "slow": 1}[speed]
    if promo and random.random() < 0.25:
        base += 1          # promo nudges multi-unit purchase
    return max(1, round(random.gauss(base, 0.8)))


# ── Inventory helpers ────────────────────────────────────────────────────────

def compute_inventory(product_id, daily_qty_map):
    """
    Given a dict {date_str: total_qty_sold}, compute per-day inventory fields.
    opening_stock starts at a realistic level and is replenished periodically.
    """
    # Determine average daily demand
    qtys = list(daily_qty_map.values())
    avg_daily = sum(qtys) / len(qtys) if qtys else 5
    reorder_point = round(avg_daily * 14)   # 2-week cover
    safety_stock  = round(avg_daily * 7)    # 1-week safety
    replenish_qty = round(avg_daily * 30)   # monthly replenishment

    stock = round(avg_daily * 45)           # start with ~45 days stock
    inv = {}
    for ds in sorted(daily_qty_map):
        sold = daily_qty_map[ds]
        opening = stock
        # replenish if below reorder point (simulating lead-time order arrival)
        purchases = 0
        if stock <= reorder_point:
            purchases = replenish_qty
            stock += purchases
        stock = max(0, stock - sold)
        inv[ds] = {
            "opening_stock": opening,
            "purchases":     purchases,
            "current_stock": stock,
            "reorder_point": reorder_point,
            "safety_stock":  safety_stock,
        }
    return inv


# ── Row builder ──────────────────────────────────────────────────────────────

FIELDNAMES = [
    "sale_id", "shop_id", "shop_name",
    "product_id", "product_name", "category", "subcategory",
    "brand", "gender", "size", "color", "material",
    "supplier_id", "supplier_name", "lead_time_days",
    "date", "day_of_week", "month", "quarter",
    "is_weekend", "is_holiday", "holiday_name", "season",
    "quantity", "unit_price", "cost_price",
    "discount_percent", "discount_amount",
    "promotion", "promotion_type",
    "total_sales", "profit",
    "opening_stock", "purchases", "current_stock",
    "reorder_point", "safety_stock",
]


def build_row(sale_id, shop, prod_tuple, d, qty, unit_price, cost_price,
              disc_pct, promo, promo_type, is_holiday, holiday_name,
              season, supplier, inv_day):

    gross     = round(qty * unit_price, 2)
    disc_amt  = round(gross * disc_pct / 100, 2)
    total_s   = round(gross - disc_amt, 2)
    profit    = round(total_s - qty * cost_price, 2)

    (pid, pname, cat, subcat, brand, gender, size, color, material,
     _up, _cp, _base, _peak, _sup_idx, _speed) = prod_tuple

    return {
        "sale_id":          f"TF{sale_id:08d}",
        "shop_id":          shop["shop_id"],
        "shop_name":        shop["shop_name"],
        "product_id":       pid,
        "product_name":     pname,
        "category":         cat,
        "subcategory":      subcat,
        "brand":            brand,
        "gender":           gender,
        "size":             size,
        "color":            color,
        "material":         material,
        "supplier_id":      supplier["supplier_id"],
        "supplier_name":    supplier["supplier_name"],
        "lead_time_days":   supplier["lead_time_days"],
        "date":             d.strftime("%Y-%m-%d"),
        "day_of_week":      d.weekday(),
        "month":            d.month,
        "quarter":          (d.month - 1) // 3 + 1,
        "is_weekend":       1 if d.weekday() >= 5 else 0,
        "is_holiday":       1 if is_holiday else 0,
        "holiday_name":     holiday_name,
        "season":           season,
        "quantity":         qty,
        "unit_price":       unit_price,
        "cost_price":       cost_price,
        "discount_percent": disc_pct,
        "discount_amount":  disc_amt,
        "promotion":        1 if promo else 0,
        "promotion_type":   promo_type,
        "total_sales":      total_s,
        "profit":           profit,
        "opening_stock":    inv_day["opening_stock"],
        "purchases":        inv_day["purchases"],
        "current_stock":    inv_day["current_stock"],
        "reorder_point":    inv_day["reorder_point"],
        "safety_stock":     inv_day["safety_stock"],
    }


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Thakur Footwear — 5 Lakh Row Dataset Generator")
    print(f"Products : {len(PRODUCTS)}")
    print(f"Days     : {NUM_DAYS}  ({START_DATE} to {END_DATE})")
    print("Pass 1   : computing per-product daily transaction counts ...")

    # ── Pass 1: figure out the raw total so we can compute a scale factor ──
    all_dates = [START_DATE + timedelta(days=i) for i in range(NUM_DAYS)]

    # Pre-compute day-level context (same for all products)
    day_ctx = {}
    for d in all_dates:
        is_hol, hol_name, fest_boost = get_festival(d)
        is_weekend = d.weekday() >= 5
        season = get_season(d)
        promo, promo_type, promo_disc = promotion_for_day(d, is_hol, hol_name, is_weekend)
        day_ctx[d] = (is_hol, hol_name, fest_boost, is_weekend, season,
                      promo, promo_type, promo_disc)

    # Count raw transactions per product per day
    raw_total = 0
    prod_day_counts = {}   # (prod_idx, date) -> txn_count

    for pi, prod in enumerate(PRODUCTS):
        (pid, pname, cat, subcat, brand, gender, size, color, material,
         unit_price, cost_price, base_txn, peak, sup_idx, speed) = prod
        for d in all_dates:
            (is_hol, hol_name, fest_boost, is_weekend, season,
             promo, promo_type, promo_disc) = day_ctx[d]
            cnt = txn_count_for_day(base_txn, peak, speed, season,
                                     is_weekend, fest_boost, promo, promo_disc, d)
            prod_day_counts[(pi, d)] = cnt
            raw_total += cnt

    print(f"  Raw total transactions : {raw_total:,}")

    # Scale factor so we hit ~500 000
    scale = TARGET_ROWS / max(raw_total, 1)
    print(f"  Scale factor           : {scale:.4f}")

    # ── Pass 2: generate rows ─────────────────────────────────────────────
    print("Pass 2   : generating rows ...")

    # We need inventory per product — first collect daily totals
    # (qty sold per product per date) then compute inventory
    prod_daily_qty = {pi: {} for pi in range(len(PRODUCTS))}

    # First sub-pass: determine final txn counts after scaling
    final_counts = {}
    for pi in range(len(PRODUCTS)):
        for d in all_dates:
            raw = prod_day_counts[(pi, d)]
            scaled = max(0, round(raw * scale))
            final_counts[(pi, d)] = scaled

    # Compute daily qty totals for inventory
    for pi, prod in enumerate(PRODUCTS):
        (pid, pname, cat, subcat, brand, gender, size, color, material,
         unit_price, cost_price, base_txn, peak, sup_idx, speed) = prod
        for d in all_dates:
            cnt = final_counts[(pi, d)]
            total_qty = sum(qty_per_txn(speed,
                                         day_ctx[d][5],
                                         day_ctx[d][7])
                            for _ in range(cnt))
            prod_daily_qty[pi][d.strftime("%Y-%m-%d")] = total_qty

    # Compute inventory for each product
    print("Pass 3   : computing inventory ...")
    prod_inv = {}
    for pi in range(len(PRODUCTS)):
        prod_inv[pi] = compute_inventory(PRODUCTS[pi][0], prod_daily_qty[pi])

    # ── Write rows ────────────────────────────────────────────────────────
    print(f"Pass 4   : writing {OUTPUT_FULL} ...")
    sale_id = 1
    total_written = 0

    with open(OUTPUT_FULL, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for d in all_dates:
            (is_hol, hol_name, fest_boost, is_weekend, season,
             promo, promo_type, promo_disc) = day_ctx[d]
            ds = d.strftime("%Y-%m-%d")

            for pi, prod in enumerate(PRODUCTS):
                (pid, pname, cat, subcat, brand, gender, size, color, material,
                 unit_price, cost_price, base_txn, peak, sup_idx, speed) = prod
                supplier = SUPPLIERS[sup_idx]
                cnt = final_counts[(pi, d)]
                inv_day = prod_inv[pi].get(ds, {
                    "opening_stock": 0, "purchases": 0, "current_stock": 0,
                    "reorder_point": 0, "safety_stock": 0,
                })

                for _ in range(cnt):
                    qty = qty_per_txn(speed, promo, promo_disc)
                    # small price variation per transaction (±3%)
                    up = round(unit_price * random.uniform(0.97, 1.03), 2)
                    cp = round(cost_price * random.uniform(0.97, 1.03), 2)
                    # ensure cost < selling price
                    if cp >= up:
                        cp = round(up * 0.60, 2)

                    row = build_row(
                        sale_id, SHOP, prod, d, qty, up, cp,
                        promo_disc, promo, promo_type,
                        is_hol, hol_name, season, supplier, inv_day
                    )
                    writer.writerow(row)
                    sale_id += 1
                    total_written += 1

    print(f"  Written : {total_written:,} rows → {OUTPUT_FULL}")

    # ── Sample file ───────────────────────────────────────────────────────
    print(f"Writing sample → {OUTPUT_SAMPLE} ...")
    with open(OUTPUT_FULL, "r", encoding="utf-8") as fin, \
         open(OUTPUT_SAMPLE, "w", newline="", encoding="utf-8") as fout:
        reader = csv.reader(fin)
        writer2 = csv.writer(fout)
        header = next(reader)
        writer2.writerow(header)
        step = max(1, total_written // 1000)
        count = 0
        for i, row in enumerate(reader):
            if i % step == 0:
                writer2.writerow(row)
                count += 1
                if count >= 1000:
                    break
    print(f"  Sample  : {count} rows → {OUTPUT_SAMPLE}")

    # ── Validation ────────────────────────────────────────────────────────
    print("\n── Validation ──────────────────────────────────────────────")
    import csv as _csv

    dates_seen = set()
    products_seen = set()
    shops_seen = set()
    neg_price = neg_profit_extreme = bad_discount = cost_gt_price = 0
    total_rows = 0
    revenue_total = 0.0

    with open(OUTPUT_FULL, "r", encoding="utf-8") as f:
        reader = _csv.DictReader(f)
        for row in reader:
            total_rows += 1
            dates_seen.add(row["date"])
            products_seen.add(row["product_id"])
            shops_seen.add(row["shop_id"])
            up   = float(row["unit_price"])
            cp   = float(row["cost_price"])
            disc = float(row["discount_percent"])
            ts   = float(row["total_sales"])
            revenue_total += ts
            if up < 0 or cp < 0:
                neg_price += 1
            if not (0 <= disc <= 100):
                bad_discount += 1
            if cp >= up:
                cost_gt_price += 1

    print(f"  Total rows          : {total_rows:,}  (target ~500,000)")
    print(f"  Date range          : {min(dates_seen)} to {max(dates_seen)}")
    print(f"  Unique dates        : {len(dates_seen)}  (expected 365)")
    print(f"  Unique products     : {len(products_seen)}")
    print(f"  Unique shops        : {len(shops_seen)}  (expected 1)")
    print(f"  Total revenue       : ₹{revenue_total:,.0f}")
    print(f"  Negative prices     : {neg_price}  (expected 0)")
    print(f"  Bad discounts       : {bad_discount}  (expected 0)")
    print(f"  Cost >= price rows  : {cost_gt_price}  (expected 0)")
    print(f"  Min records/product : {total_rows // max(len(products_seen),1)} avg per product")

    ok = (
        abs(total_rows - TARGET_ROWS) / TARGET_ROWS < 0.05
        and len(dates_seen) == 365
        and len(shops_seen) == 1
        and neg_price == 0
        and bad_discount == 0
        and cost_gt_price == 0
    )
    print(f"\n  VALIDATION {'PASSED' if ok else 'FAILED'}")
    if not ok:
        if abs(total_rows - TARGET_ROWS) / TARGET_ROWS >= 0.05:
            print(f"  ! Row count {total_rows:,} is >5% off target {TARGET_ROWS:,}")
        if len(dates_seen) != 365:
            print(f"  ! Expected 365 dates, got {len(dates_seen)}")
        if len(shops_seen) != 1:
            print(f"  ! Expected 1 shop, got {len(shops_seen)}: {shops_seen}")

    print("\nDone.")


if __name__ == "__main__":
    main()
