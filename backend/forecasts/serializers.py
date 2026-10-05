from rest_framework import serializers
from .models import Forecast, ModelEvaluation

class ForecastSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category = serializers.CharField(source='product.category', read_only=True)

    class Meta:
        model = Forecast
        fields = '__all__'

class ModelEvaluationSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    category = serializers.CharField(source='product.category', read_only=True)

    class Meta:
        model = ModelEvaluation
        fields = '__all__'
