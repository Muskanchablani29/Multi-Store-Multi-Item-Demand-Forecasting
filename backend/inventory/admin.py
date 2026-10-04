from django.contrib import admin
from .models import Inventory

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'current_stock', 'reorder_point', 'updated_at')
    list_filter = ('shop',)
    search_fields = ('shop__name', 'product__name')
