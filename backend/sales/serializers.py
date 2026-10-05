from rest_framework import serializers
from .models import Sale

class SaleSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category = serializers.CharField(source='product.category', read_only=True)
    brand = serializers.CharField(source='product.brand', read_only=True)

    class Meta:
        model = Sale
        fields = '__all__'
