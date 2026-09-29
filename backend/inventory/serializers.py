from rest_framework import serializers
from .models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    needs_reorder = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = '__all__'

    def get_needs_reorder(self, obj):
        return obj.current_stock <= obj.reorder_point
