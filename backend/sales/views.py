import csv
import io
import os
import time
from datetime import date as date_type
from django.conf import settings
from django.http import FileResponse, Http404
from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Sale
from .serializers import SaleSerializer
from shops.models import Shop
from products.models import Product

STATS_CACHE_KEY = 'dashboard_stats'
STATS_CACHE_TTL = 300  # 5 minutes

DATASET_FILES = {
    'full':   'thakur_footwear_sales_500k.csv',
    'sample': 'thakur_footwear_sample.csv',
}

REQUIRED_COLS = {'shop_name', 'date', 'quantity'}

SEASONS = {
    1: 'Winter', 2: 'Winter', 3: 'Summer', 4: 'Summer', 5: 'Summer',
    6: 'Monsoon', 7: 'Monsoon', 8: 'Monsoon', 9: 'Monsoon',
    10: 'Festival', 11: 'Festival', 12: 'Winter'
}


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('shop', 'product').all()
    serializer_class = SaleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        shop_id = self.request.query_params.get('shop_id')
        product_id = self.request.query_params.get('product_id')
        category = self.request.query_params.get('category')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        if category:
            qs = qs.filter(product__category=category)
        return qs

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        # Serve from cache if available (recomputed every 5 min or after upload)
        cached = cache.get(STATS_CACHE_KEY)
        if cached:
            return Response(cached)

        qs = Sale.objects.all()
        # Single aggregate query for all totals
        totals = qs.aggregate(
            total_revenue=Sum('total_sales'),
            total_units=Sum('quantity'),
            total_profit=Sum('profit'),
        )
        total_revenue  = totals['total_revenue'] or 0
        total_units    = totals['total_units']   or 0
        total_profit   = totals['total_profit']  or 0
        total_records  = qs.count()
        total_shops    = Shop.objects.count()
        total_products = Product.objects.count()

        category_sales = list(
            qs.values('product__category')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('-revenue')
        )
        brand_sales = list(
            qs.values('product__brand')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('-revenue')[:10]
        )
        shop_sales = list(
            qs.values('shop__name')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('-revenue')
        )
        top_products = list(
            qs.values('product__name', 'product__category')
            .annotate(units=Sum('quantity'))
            .order_by('-units')[:10]
        )
        season_sales = list(
            qs.values('season')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
            .order_by('-revenue')
        )
        promo_sales = list(
            qs.values('promotion')
            .annotate(units=Sum('quantity'), revenue=Sum('total_sales'))
        )
        # Recent sales — last 10 rows only, never the full table
        recent_sales = list(
            qs.select_related('shop', 'product')
            .order_by('-date', '-id')[:10]
            .values(
                'shop__name', 'product__name', 'product__category',
                'date', 'quantity', 'total_sales'
            )
        )
        for r in recent_sales:
            r['shop_name']    = r.pop('shop__name')
            r['product_name'] = r.pop('product__name')
            r['category']     = r.pop('product__category')
            r['date']         = str(r['date'])

        result = {
            'total_revenue':  round(total_revenue, 2),
            'total_units':    round(total_units, 0),
            'total_profit':   round(total_profit, 2),
            'total_records':  total_records,
            'total_shops':    total_shops,
            'total_products': total_products,
            'category_sales': category_sales,
            'brand_sales':    brand_sales,
            'shop_sales':     shop_sales,
            'top_products':   top_products,
            'season_sales':   season_sales,
            'promo_sales':    promo_sales,
            'recent_sales':   recent_sales,
        }
        cache.set(STATS_CACHE_KEY, result, STATS_CACHE_TTL)
        return Response(result)

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = file.read().decode('utf-8')
        except Exception:
            return Response({'error': 'File encoding error. Use UTF-8.'}, status=400)

        reader = csv.DictReader(io.StringIO(decoded))
        headers = set(reader.fieldnames or [])

        missing = REQUIRED_COLS - headers
        if missing:
            return Response({'error': f"Missing required columns: {', '.join(missing)}"}, status=400)

        created = 0
        errors = []

        for i, row in enumerate(reader, start=2):
            row_errors = _validate_row(row, i)
            if row_errors:
                errors.extend(row_errors)
                continue
            try:
                shop_id_val = row.get('shop_id', '').strip() or None
                shop_name = row['shop_name'].strip()
                shop_location = row.get('shop_location', '').strip()

                if shop_id_val:
                    shop, _ = Shop.objects.get_or_create(
                        shop_id=shop_id_val,
                        defaults={'name': shop_name, 'location': shop_location}
                    )
                else:
                    shop, _ = Shop.objects.get_or_create(
                        name=shop_name,
                        defaults={'location': shop_location, 'shop_id': None}
                    )

                product_id_val = row.get('product_id', '').strip() or None
                product_name = row.get('item_name', row.get('product_name', '')).strip()

                product_defaults = {
                    'category': row.get('category', '').strip(),
                    'subcategory': row.get('subcategory', '').strip(),
                    'brand': row.get('brand', '').strip(),
                    'gender': row.get('gender', '').strip(),
                    'size': row.get('size', '').strip(),
                    'color': row.get('color', '').strip(),
                    'material': row.get('material', '').strip(),
                }
                if row.get('unit_price'):
                    product_defaults['unit_price'] = float(row['unit_price'])
                if row.get('cost_price'):
                    product_defaults['cost_price'] = float(row['cost_price'])
                if row.get('supplier_id'):
                    product_defaults['supplier_id'] = row['supplier_id'].strip() or None
                if row.get('supplier_name'):
                    product_defaults['supplier_name'] = row['supplier_name'].strip()
                if row.get('lead_time_days'):
                    product_defaults['lead_time_days'] = int(float(row['lead_time_days']))

                if product_id_val:
                    product, _ = Product.objects.get_or_create(
                        product_id=product_id_val,
                        defaults={'name': product_name, **product_defaults}
                    )
                else:
                    product, _ = Product.objects.get_or_create(
                        name=product_name,
                        defaults={'product_id': None, **product_defaults}
                    )

                qty = float(row['quantity'])
                unit_price = float(row.get('unit_price') or product.unit_price or 0)
                cost_price = float(row.get('cost_price') or product.cost_price or 0)
                discount_pct = float(row.get('discount_percent') or 0)
                gross = qty * unit_price
                disc_amt = gross * discount_pct / 100
                total_sales = gross - disc_amt
                profit = total_sales - (qty * cost_price)

                promo_raw = row.get('promotion', '').strip().lower()
                promotion = promo_raw in ('1', 'true', 'yes')
                promotion_type = row.get('promotion_type', 'No Promotion').strip() or 'No Promotion'
                promo_discount = float(row.get('promotion_discount') or 0)

                holiday_raw = row.get('holiday', row.get('is_holiday', '')).strip().lower()
                is_holiday = holiday_raw in ('1', 'true', 'yes')
                holiday_name = row.get('holiday_name', '').strip()

                from datetime import datetime
                d = datetime.strptime(row['date'].strip(), '%Y-%m-%d').date()
                season = row.get('season', SEASONS.get(d.month, '')).strip()
                day_of_week = d.weekday()
                is_weekend = day_of_week >= 5
                month = d.month
                week_number = d.isocalendar()[1]

                Sale.objects.create(
                    shop=shop,
                    product=product,
                    date=d,
                    quantity=qty,
                    unit_price=unit_price,
                    cost_price=cost_price,
                    discount_percent=discount_pct,
                    discount_amount=disc_amt,
                    total_sales=total_sales,
                    profit=profit,
                    promotion=promotion,
                    promotion_type=promotion_type,
                    promotion_discount=promo_discount,
                    is_holiday=is_holiday,
                    holiday_name=holiday_name,
                    season=season,
                    day_of_week=day_of_week,
                    is_weekend=is_weekend,
                    month=month,
                    week_number=week_number,
                )
                created += 1
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")

        cache.delete(STATS_CACHE_KEY)  # invalidate dashboard cache after upload
        return Response({'created': created, 'errors': errors[:50]}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='download', permission_classes=[__import__('rest_framework').permissions.AllowAny])
    def download_dataset(self, request):
        """Stream a pre-generated Thakur Footwear CSV for download.
        ?type=full   → thakur_footwear_sales_500k.csv  (default)
        ?type=sample → thakur_footwear_sample.csv
        No auth required so the browser download link works directly.
        """
        file_type = request.query_params.get('type', 'full')
        if file_type not in DATASET_FILES:
            return Response({'error': 'type must be full or sample'}, status=400)

        filename = DATASET_FILES[file_type]
        filepath = os.path.join(settings.DATASETS_DIR, filename)

        if not os.path.exists(filepath):
            raise Http404(f'{filename} not found on server. Run generate_thakur_footwear.py first.')

        response = FileResponse(
            open(filepath, 'rb'),
            content_type='text/csv',
            as_attachment=True,
            filename=filename,
        )
        return response


def _validate_row(row, i):
    errs = []
    qty_raw = row.get('quantity', '').strip()
    if not qty_raw:
        errs.append(f"Row {i}: quantity is missing")
    else:
        try:
            if float(qty_raw) < 0:
                errs.append(f"Row {i}: quantity cannot be negative")
        except ValueError:
            errs.append(f"Row {i}: quantity must be numeric")

    date_raw = row.get('date', '').strip()
    if not date_raw:
        errs.append(f"Row {i}: date is missing")
    else:
        try:
            from datetime import datetime
            datetime.strptime(date_raw, '%Y-%m-%d')
        except ValueError:
            errs.append(f"Row {i}: date must be YYYY-MM-DD, got '{date_raw}'")

    for price_col in ('unit_price', 'cost_price'):
        val = row.get(price_col, '').strip()
        if val:
            try:
                if float(val) < 0:
                    errs.append(f"Row {i}: {price_col} cannot be negative")
            except ValueError:
                errs.append(f"Row {i}: {price_col} must be numeric")

    disc = row.get('discount_percent', '').strip()
    if disc:
        try:
            d = float(disc)
            if not (0 <= d <= 100):
                errs.append(f"Row {i}: discount_percent must be 0–100")
        except ValueError:
            errs.append(f"Row {i}: discount_percent must be numeric")

    if not row.get('shop_name', '').strip():
        errs.append(f"Row {i}: shop_name is missing")

    product_name = row.get('item_name', row.get('product_name', '')).strip()
    if not product_name:
        errs.append(f"Row {i}: product_name (or item_name) is missing")

    return errs
