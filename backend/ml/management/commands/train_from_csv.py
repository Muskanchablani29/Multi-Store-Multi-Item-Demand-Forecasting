"""
management command: train_from_csv
Expects the cleaned CSV produced by preprocess_dataset.py.

Usage:
    python manage.py train_from_csv
    python manage.py train_from_csv --csv path/to/thakur_footwear_cleaned.csv
    python manage.py train_from_csv --product-id 5          # train one product
    python manage.py train_from_csv --skip-import           # DB already loaded
"""

import csv
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from forecasts.models import ModelEvaluation
from ml.engine import train_and_evaluate
from products.models import Product
from sales.models import Sale
from shops.models import Shop

SEASONS = {
    1: 'Winter', 2: 'Winter', 3: 'Summer', 4: 'Summer', 5: 'Summer',
    6: 'Monsoon', 7: 'Monsoon', 8: 'Monsoon', 9: 'Monsoon',
    10: 'Festival', 11: 'Festival', 12: 'Winter',
}

DEFAULT_CSV = settings.BASE_DIR.parent / 'thakur_footwear_cleaned.csv'


class Command(BaseCommand):
    help = 'Import CSV sales data and train LSTM models for every product.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', default=str(DEFAULT_CSV), help='Path to CSV file')
        parser.add_argument('--product-id', type=int, default=None,
                            help='Train only this DB product id (skip others)')
        parser.add_argument('--skip-import', action='store_true',
                            help='Skip CSV import; use data already in DB')

    # ------------------------------------------------------------------ #
    def handle(self, *args, **options):
        models_dir = str(settings.ML_MODELS_DIR)

        if not options['skip_import']:
            self._import_csv(options['csv'])

        self._train_all(models_dir, only_product_id=options['product_id'])

    # ------------------------------------------------------------------ #
    def _import_csv(self, csv_path):
        path = Path(csv_path)
        if not path.exists():
            self.stderr.write(self.style.ERROR(f'CSV not found: {path}'))
            return

        self.stdout.write(f'Importing {path.name} …')

        with open(path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.stdout.write(f'  {len(rows):,} rows read — upserting shops/products/sales …')

        shop_cache    = {}   # shop_id_str → Shop
        product_cache = {}   # (shop.pk, product_name) → Product
        sales_bulk    = []
        created = skipped = 0

        for i, row in enumerate(rows, 1):
            try:
                # ── Shop ──────────────────────────────────────────────
                sid = row.get('shop_id', '').strip() or 'TF001'
                if sid not in shop_cache:
                    shop, _ = Shop.objects.get_or_create(
                        shop_id=sid,
                        defaults={
                            'name':     row.get('shop_name', sid).strip(),
                            'location': row.get('shop_location', '').strip(),
                            'category': 'Footwear',
                        },
                    )
                    shop_cache[sid] = shop
                shop = shop_cache[sid]

                # ── Product ───────────────────────────────────────────
                pname = row.get('product_name', row.get('item_name', '')).strip()
                if not pname:
                    skipped += 1
                    continue

                pkey = (shop.pk, pname)
                if pkey not in product_cache:
                    pid_val = row.get('product_id', '').strip() or None
                    product, _ = Product.objects.get_or_create(
                        shop=shop,
                        name=pname,
                        defaults={
                            'product_id':    pid_val,
                            'category':      row.get('category', '').strip(),
                            'subcategory':   row.get('subcategory', '').strip(),
                            'brand':         row.get('brand', '').strip(),
                            'gender':        row.get('gender', '').strip(),
                            'size':          row.get('size', '').strip(),
                            'color':         row.get('color', '').strip(),
                            'material':      row.get('material', '').strip(),
                            'unit_price':    float(row.get('unit_price') or 0),
                            'cost_price':    float(row.get('cost_price') or 0),
                            'supplier_id':   row.get('supplier_id', '').strip(),
                            'supplier_name': row.get('supplier_name', '').strip(),
                            'lead_time_days':int(float(row.get('lead_time_days') or 7)),
                        },
                    )
                    product_cache[pkey] = product
                product = product_cache[pkey]

                # ── Sale row ──────────────────────────────────────────
                qty = float(row.get('quantity', 0))
                if qty <= 0:
                    skipped += 1
                    continue

                d = datetime.strptime(row['date'].strip(), '%Y-%m-%d').date()

                unit_price   = float(row.get('unit_price') or product.unit_price or 0)
                cost_price   = float(row.get('cost_price') or product.cost_price or 0)
                disc_pct     = float(row.get('discount_percent') or 0)
                gross        = qty * unit_price
                disc_amt     = gross * disc_pct / 100
                total_sales  = gross - disc_amt
                profit       = total_sales - (qty * cost_price)

                # cleaned CSV has int 0/1 for boolean cols
                promotion    = int(float(row.get('promotion', 0) or 0)) == 1
                promo_type   = row.get('promotion_type', 'No Promotion').strip() or 'No Promotion'
                promo_disc   = float(row.get('promotion_discount') or 0)

                is_holiday   = int(float(row.get('is_holiday', 0) or 0)) == 1
                holiday_name = row.get('holiday_name', '').strip()

                # trust recomputed time features from preprocess_dataset.py
                dow          = int(row.get('day_of_week', d.weekday()))
                is_weekend   = int(float(row.get('is_weekend', 0) or 0)) == 1
                month        = int(row.get('month', d.month))
                season       = row.get('season', SEASONS.get(month, '')).strip()
                week_num     = d.isocalendar()[1]

                sales_bulk.append(Sale(
                    shop=shop, product=product, date=d,
                    quantity=qty, unit_price=unit_price, cost_price=cost_price,
                    discount_percent=disc_pct, discount_amount=disc_amt,
                    total_sales=total_sales, profit=profit,
                    promotion=promotion, promotion_type=promo_type,
                    promotion_discount=promo_disc,
                    is_holiday=is_holiday, holiday_name=holiday_name,
                    season=season, day_of_week=dow, is_weekend=is_weekend,
                    month=month, week_number=week_num,
                ))
                created += 1

                # Bulk-insert every 5 000 rows to keep memory low
                if len(sales_bulk) >= 5000:
                    Sale.objects.bulk_create(sales_bulk, ignore_conflicts=True)
                    sales_bulk.clear()
                    self.stdout.write(f'  … {i:,} rows processed', ending='\r')

            except Exception as e:
                skipped += 1
                if skipped <= 5:
                    self.stderr.write(f'  Row {i} skipped: {e}')

        if sales_bulk:
            Sale.objects.bulk_create(sales_bulk, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(
            f'  Import done — {created:,} sales created, {skipped:,} skipped.'
        ))

    # ------------------------------------------------------------------ #
    def _train_all(self, models_dir, only_product_id=None):
        products = Product.objects.all()
        if only_product_id:
            products = products.filter(pk=only_product_id)

        total = products.count()
        self.stdout.write(f'\nTraining LSTM for {total} product(s) …\n')

        ok = failed = 0
        for idx, product in enumerate(products, 1):
            shop = product.shop
            if not shop:
                self.stderr.write(f'  [{idx}/{total}] {product.name} — no shop linked, skip')
                failed += 1
                continue

            sales_qs = Sale.objects.filter(shop=shop, product=product)
            label = f'[{idx}/{total}] {product.name} (shop={shop.name})'

            try:
                result = train_and_evaluate(sales_qs, shop.pk, product.pk, models_dir)

                ModelEvaluation.objects.update_or_create(
                    shop=shop, product=product, model_type='LSTM',
                    defaults={
                        'mae':  result['mae'],
                        'mse':  result['mse'],
                        'rmse': result['rmse'],
                        'r2':   result['r2'],
                    },
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'  {label} — RMSE={result["rmse"]:.4f}  R²={result["r2"]:.4f}'
                        f'  (train={result["train_days"]}d / test={result["test_days"]}d)'
                    )
                )
                ok += 1

            except Exception as e:
                self.stderr.write(self.style.WARNING(f'  {label} — FAILED: {e}'))
                failed += 1

        self.stdout.write(f'\nDone — {ok} trained, {failed} failed.')
