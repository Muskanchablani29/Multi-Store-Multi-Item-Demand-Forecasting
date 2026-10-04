from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'date', 'quantity')
    list_filter = ('shop', 'product', 'date')
    search_fields = ('shop__name', 'product__name')
    date_hierarchy = 'date'
