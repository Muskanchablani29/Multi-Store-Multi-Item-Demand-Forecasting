from django.db import models
from shops.models import Shop
from products.models import Product

class Forecast(models.Model):
    MODEL_CHOICES = [('LSTM', 'LSTM'), ('GRU', 'GRU')]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='forecasts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts')
    model_type = models.CharField(max_length=10, choices=MODEL_CHOICES)
    forecast_date = models.DateField()
    predicted_qty = models.FloatField()
    actual_qty = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['forecast_date']

class ModelEvaluation(models.Model):
    MODEL_CHOICES = [('LSTM', 'LSTM'), ('GRU', 'GRU')]
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    model_type = models.CharField(max_length=10, choices=MODEL_CHOICES)
    mae = models.FloatField()
    mse = models.FloatField()
    rmse = models.FloatField()
    r2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
