import django, os, random, datetime
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from shops.models import Shop
from products.models import Product
from sales.models import Sale

shop, _ = Shop.objects.get_or_create(name='ML Test Shop', defaults={'shop_id': 'ML001'})
product, _ = Product.objects.get_or_create(
    name='ML Test Shoe',
    defaults={'product_id': 'P001', 'category': 'Sports', 'unit_price': 999, 'cost_price': 600}
)
print('shop id=%d  product id=%d' % (shop.id, product.id))

base = datetime.date(2023, 1, 1)
for i in range(100):
    d = base + datetime.timedelta(days=i)
    qty = 5 + random.randint(0, 10) + (3 if d.weekday() >= 5 else 0)
    Sale.objects.get_or_create(
        shop=shop, product=product, date=d,
        defaults={
            'quantity': qty, 'unit_price': 999, 'cost_price': 600,
            'discount_percent': 0, 'discount_amount': 0,
            'total_sales': qty * 999, 'profit': qty * 399,
            'promotion': False, 'is_holiday': False,
            'season': 'Summer', 'day_of_week': d.weekday(),
            'is_weekend': d.weekday() >= 5, 'month': d.month,
            'week_number': d.isocalendar()[1],
        }
    )

count = Sale.objects.filter(shop=shop, product=product).count()
print('Sales seeded: %d' % count)
