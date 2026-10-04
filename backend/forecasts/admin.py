from django.contrib import admin
from .models import Forecast, ModelEvaluation

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'model_type', 'forecast_date', 'predicted_qty', 'actual_qty', 'created_at')
    list_filter = ('model_type', 'shop', 'product')
    date_hierarchy = 'forecast_date'

@admin.register(ModelEvaluation)
class ModelEvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'model_type', 'mae', 'mse', 'rmse', 'r2', 'created_at')
    list_filter = ('model_type', 'shop', 'product')
