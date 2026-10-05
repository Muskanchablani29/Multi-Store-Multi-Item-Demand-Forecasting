from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from sales.models import Sale
from forecasts.models import Forecast, ModelEvaluation
from shops.models import Shop
from products.models import Product
from .engine import train_and_evaluate, forecast_future
import datetime


class TrainModelView(APIView):
    def post(self, request):
        shop_id = request.data.get('shop_id')
        product_id = request.data.get('product_id')
        model_type = request.data.get('model_type', 'LSTM').upper()

        if model_type not in ('LSTM', 'GRU'):
            return Response({'error': 'model_type must be LSTM or GRU'}, status=400)

        sales_qs = Sale.objects.filter(shop_id=shop_id, product_id=product_id)
        if not sales_qs.exists():
            return Response({'error': 'No sales data found'}, status=404)

        try:
            result = train_and_evaluate(
                sales_qs, shop_id, product_id, model_type,
                str(settings.ML_MODELS_DIR)
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        shop = Shop.objects.get(id=shop_id)
        product = Product.objects.get(id=product_id)

        ModelEvaluation.objects.update_or_create(
            shop=shop, product=product, model_type=model_type,
            defaults={
                'mae': result['mae'], 'mse': result['mse'],
                'rmse': result['rmse'], 'r2': result['r2']
            }
        )

        return Response({
            'metrics': {'mae': result['mae'], 'mse': result['mse'], 'rmse': result['rmse'], 'r2': result['r2']},
            'actual':    result['actual'],
            'predicted': result['predicted'],
            'dates':     result['dates'],
            'train_days': result.get('train_days'),
            'test_days':  result.get('test_days'),
            'total_days': result.get('total_days'),
        })


class ForecastView(APIView):
    def post(self, request):
        shop_id = request.data.get('shop_id')
        product_id = request.data.get('product_id')
        model_type = request.data.get('model_type', 'LSTM').upper()
        steps = int(request.data.get('steps', 30))

        sales_qs = Sale.objects.filter(shop_id=shop_id, product_id=product_id)
        if not sales_qs.exists():
            return Response({'error': 'No sales data found'}, status=404)

        try:
            forecasts = forecast_future(
                sales_qs, shop_id, product_id, model_type,
                steps, str(settings.ML_MODELS_DIR)
            )
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=400)

        shop = Shop.objects.get(id=shop_id)
        product = Product.objects.get(id=product_id)

        Forecast.objects.filter(shop=shop, product=product, model_type=model_type).delete()
        forecast_objs = [
            Forecast(shop=shop, product=product, model_type=model_type,
                     forecast_date=date, predicted_qty=qty)
            for date, qty in forecasts
        ]
        Forecast.objects.bulk_create(forecast_objs)

        return Response({
            'forecasts': [{'date': d, 'predicted_qty': q} for d, q in forecasts]
        })
