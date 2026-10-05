import django, os, time, json
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
import urllib.request

user = User.objects.first()
token = str(AccessToken.for_user(user))

req = urllib.request.Request(
    'http://localhost:8000/api/sales/stats/',
    headers={'Authorization': f'Bearer {token}'}
)
t0 = time.time()
with urllib.request.urlopen(req) as resp:
    body = resp.read()
elapsed = time.time() - t0

data = json.loads(body)
print(f"Status  : 200")
print(f"Time    : {elapsed:.2f}s")
print(f"Size    : {len(body)/1024:.1f} KB")
print(f"Keys    : {list(data.keys())}")
print(f"Shops   : {data.get('total_shops')}")
print(f"Products: {data.get('total_products')}")
print(f"Records : {data.get('total_records')}")
print(f"Recent  : {len(data.get('recent_sales', []))} rows")
