from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/shops/', include('shops.urls')),
    path('api/products/', include('products.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/forecasts/', include('forecasts.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/ml/', include('ml.urls')),
]
