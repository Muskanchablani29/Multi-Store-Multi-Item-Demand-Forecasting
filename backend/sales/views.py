import csv
import io
from datetime import datetime, date as date_type
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer
from shops.models import Shop
from products.models import Product

SEASONS = {
    1: 'Winter', 2: 'Winter', 3: 'Summer', 4: 'Summer', 5: 'Summer',
    6: 'Monsoon', 7: 'Monsoon', 8: 'Monsoon', 9: 'Monsoon',
    10: 'Festival', 11: 'Festival', 12: 'Winter',
}


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class SaleViewSet(viewsets.ModelViewSet):
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shop = _get_shop(self.request.user)
        if not shop:
            return Sale.objects.none()
        return Sale.objects.select_related('shop', 'product').filter(shop=shop)

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_csv(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)

        try:
            decoded = file.read().decode('utf-8')
        except Exception:
            return Response({'error': 'File encoding error. Use UTF-8.'}, status=400)

        reader = csv.DictReader(io.StringIO(decoded))
        headers = set(reader.fieldnames or [])
        required = {'date', 'quantity'}
        missing = required - headers
        if missing:
            return Response({'error': f"Missing columns: {', '.join(missing)}"}, status=400)

        created = 0
        errors = []

        for i, row in enumerate(reader, start=2):
            try:
                product_name = row.get('product_name', row.get('item_name', '')).strip()
                if not product_name:
                    errors.append(f"Row {i}: product_name missing")
                    continue

                qty_raw = row.get('quantity', '').strip()
                if not qty_raw:
                    errors.append(f"Row {i}: quantity missing")
                    continue
                qty = float(qty_raw)
                if qty < 0:
                    errors.append(f"Row {i}: quantity cannot be negative")
                    continue

                date_raw = row.get('date', '').strip()
                d = datetime.strptime(date_raw, '%Y-%m-%d').date()

                product_id_val = row.get('product_id', '').strip() or None
                product_defaults = {
                    'shop': shop,
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
                    product_defaults['supplier_id'] = row['supplier_id'].strip()
                if row.get('supplier_name'):
                    product_defaults['supplier_name'] = row['supplier_name'].strip()
                if row.get('lead_time_days'):
                    product_defaults['lead_time_days'] = int(float(row['lead_time_days']))

                product, _ = Product.objects.get_or_create(
                    shop=shop,
                    name=product_name,
                    defaults={**product_defaults, 'product_id': product_id_val},
                )

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

                holiday_raw = row.get('is_holiday', row.get('holiday', '')).strip().lower()
                is_holiday = holiday_raw in ('1', 'true', 'yes')
                holiday_name = row.get('holiday_name', '').strip()

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

        return Response({'created': created, 'errors': errors[:50]}, status=status.HTTP_201_CREATED)
