import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from sales.models import Sale
from shops.models import Shop
from products.models import Product
from django.db.models import Sum, Count, Avg

print('=== DB State ===')
print('Total sales rows :', Sale.objects.count())
print('Total shops      :', Shop.objects.count())
print('Total products   :', Product.objects.count())

print('\n=== Top 8 Shop+Product combos by row count ===')
top = (Sale.objects
       .values('shop__name', 'product__name', 'shop_id', 'product_id')
       .annotate(n=Count('id'))
       .order_by('-n')[:8])

for t in top:
    dates = (Sale.objects
             .filter(shop_id=t['shop_id'], product_id=t['product_id'])
             .values_list('date', flat=True).distinct())
    print(f"  shop_id={t['shop_id']} prod_id={t['product_id']} "
          f"rows={t['n']} unique_dates={len(dates)} "
          f"| {t['product__name'][:30]}")

print('\n=== Daily aggregation check for top combo ===')
if top:
    t = top[0]
    daily = (Sale.objects
             .filter(shop_id=t['shop_id'], product_id=t['product_id'])
             .values('date')
             .annotate(total_qty=Sum('quantity'), txns=Count('id'))
             .order_by('date'))
    qtys = [d['total_qty'] for d in daily]
    txns = [d['txns'] for d in daily]
    print(f"  Product : {t['product__name']}")
    print(f"  Days    : {len(qtys)}")
    print(f"  Qty/day : min={min(qtys):.1f}  max={max(qtys):.1f}  mean={sum(qtys)/len(qtys):.1f}")
    print(f"  Txns/day: min={min(txns)}  max={max(txns)}  mean={sum(txns)/len(txns):.1f}")
    print(f"  NOTE: engine currently trains on {t['n']} individual txn rows,")
    print(f"        NOT on {len(qtys)} aggregated daily rows — this kills accuracy!")
