import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()
from sales.models import Sale
from products.models import Product
from shops.models import Shop
from inventory.models import Inventory
print('Sales:', Sale.objects.count())
print('Products:', Product.objects.count())
print('Shops:', Shop.objects.count())
print('Inventory:', Inventory.objects.count())
