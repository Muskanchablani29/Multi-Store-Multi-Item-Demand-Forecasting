from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    shop_name        = serializers.CharField(source='shop.name',            read_only=True)
    product_name     = serializers.CharField(source='product.name',         read_only=True)
    category         = serializers.CharField(source='product.category',     read_only=True)
    brand            = serializers.CharField(source='product.brand',        read_only=True)
    needs_reorder    = serializers.SerializerMethodField()
    inventory_status = serializers.SerializerMethodField()

    class Meta:
        model  = Inventory
        fields = '__all__'

    def get_needs_reorder(self, obj):
        return obj.current_stock <= obj.reorder_point

    def get_inventory_status(self, obj):
        if obj.current_stock <= 0:
            return 'Out of Stock'
        if obj.current_stock <= obj.safety_stock:
            return 'Reorder Required'
        if obj.current_stock <= obj.reorder_point:
            return 'Low Stock'
        return 'Sufficient Stock'
