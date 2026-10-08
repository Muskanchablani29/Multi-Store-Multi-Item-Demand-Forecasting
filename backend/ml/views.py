from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.db.models import Sum
from sales.models import Sale
from forecasts.models import Forecast, ModelEvaluation
from products.models import Product
from .engine import train_and_evaluate, forecast_future
import os
import traceback


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class TrainModelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        product_id = request.data.get('product_id')
        model_type = request.data.get('model_type', 'LSTM').upper()

        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)
        if model_type not in ('LSTM', 'GRU'):
            return Response({'error': 'model_type must be LSTM or GRU'}, status=400)

        sales_qs = Sale.objects.filter(shop=shop, product_id=product_id)
        if not sales_qs.exists():
            return Response({'error': 'No sales data found for this product.'}, status=404)

        try:
            result = train_and_evaluate(
                sales_qs, shop.id, product_id, model_type,
                str(settings.ML_MODELS_DIR)
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

        product = Product.objects.get(id=product_id)
        ModelEvaluation.objects.update_or_create(
            shop=shop, product=product, model_type=model_type,
            defaults={
                'mae': result['mae'], 'mse': result['mse'],
                'rmse': result['rmse'], 'r2': result['r2'],
            }
        )

        return Response({
            'metrics':    {'mae': result['mae'], 'mse': result['mse'],
                           'rmse': result['rmse'], 'r2': result['r2']},
            'actual':     result['actual'],
            'predicted':  result['predicted'],
            'dates':      result['dates'],
            'train_days': result.get('train_days'),
            'test_days':  result.get('test_days'),
            'total_days': result.get('total_days'),
        })


class AutoTrainForecastView(APIView):
    """
    POST /api/ml/auto-train/
    Trains LSTM on every product that has enough data, then generates
    a 30-day forecast for each.  Called automatically after CSV upload.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        model_type = request.data.get('model_type', 'LSTM').upper()
        steps = int(request.data.get('steps', 30))

        products = Product.objects.filter(shop=shop)
        trained, skipped, errors = [], [], []

        for product in products:
            sales_qs = Sale.objects.filter(shop=shop, product=product)
            if not sales_qs.exists():
                skipped.append({'product_id': product.id, 'name': product.name, 'reason': 'no sales data'})
                continue
            try:
                result = train_and_evaluate(
                    sales_qs, shop.id, product.id, model_type,
                    str(settings.ML_MODELS_DIR), months=3
                )
                ModelEvaluation.objects.update_or_create(
                    shop=shop, product=product, model_type=model_type,
                    defaults={
                        'mae': result['mae'], 'mse': result['mse'],
                        'rmse': result['rmse'], 'r2': result['r2'],
                    }
                )
                # Generate forecast immediately
                forecasts = forecast_future(
                    sales_qs, shop.id, product.id, model_type,
                    steps, str(settings.ML_MODELS_DIR), months=3
                )
                Forecast.objects.filter(shop=shop, product=product, model_type=model_type).delete()
                Forecast.objects.bulk_create([
                    Forecast(shop=shop, product=product, model_type=model_type,
                             forecast_date=d, predicted_qty=q)
                    for d, q in forecasts
                ])
                trained.append({
                    'product_id': product.id,
                    'name': product.name,
                    'rmse': result['rmse'],
                    'total_days': result['total_days'],
                    'forecasts': [{'date': d, 'predicted_qty': q} for d, q in forecasts],
                })
            except ValueError as e:
                skipped.append({'product_id': product.id, 'name': product.name, 'reason': str(e)})
            except Exception as e:
                errors.append({'product_id': product.id, 'name': product.name, 'error': str(e)})

        return Response({
            'trained': trained,
            'skipped': skipped,
            'errors': errors,
            'summary': {
                'total': len(products),
                'trained': len(trained),
                'skipped': len(skipped),
                'errors': len(errors),
            }
        })


class OctoberForecastView(APIView):
    """
    POST /api/ml/next-month-forecast/
    Trains on last 3 months of data for every product, forecasts the next
    31 days, and returns per-product totals ranked by demand.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        model_type = request.data.get('model_type', 'LSTM').upper()
        STEPS = 31

        products = Product.objects.filter(shop=shop)
        results, skipped = [], []
        forecast_month_label = None

        for product in products:
            sales_qs = Sale.objects.filter(shop=shop, product=product)
            if not sales_qs.exists():
                skipped.append(product.name)
                continue
            try:
                model_path = os.path.join(
                    str(settings.ML_MODELS_DIR),
                    f"{model_type}_{shop.id}_{product.id}.keras"
                )
                train_result = None
                if not os.path.exists(model_path):
                    train_result = train_and_evaluate(
                        sales_qs, shop.id, product.id, model_type,
                        str(settings.ML_MODELS_DIR), months=3
                    )
                    ModelEvaluation.objects.update_or_create(
                        shop=shop, product=product, model_type=model_type,
                        defaults={
                            'mae': train_result['mae'], 'mse': train_result['mse'],
                            'rmse': train_result['rmse'], 'r2': train_result['r2'],
                        }
                    )
                forecasts = forecast_future(
                    sales_qs, shop.id, product.id, model_type,
                    STEPS, str(settings.ML_MODELS_DIR), months=3
                )
                Forecast.objects.filter(
                    shop=shop, product=product, model_type=model_type
                ).delete()
                Forecast.objects.bulk_create([
                    Forecast(shop=shop, product=product, model_type=model_type,
                             forecast_date=d, predicted_qty=q)
                    for d, q in forecasts
                ])
                total_qty = sum(q for _, q in forecasts)
                # Capture the forecast month label from first product
                if forecast_month_label is None and forecasts:
                    import datetime as _dt
                    first_date = _dt.datetime.strptime(forecasts[0][0], '%Y-%m-%d')
                    forecast_month_label = first_date.strftime('%B %Y')
                eval_obj = ModelEvaluation.objects.filter(
                    shop=shop, product=product, model_type=model_type
                ).first()
                results.append({
                    'product_id':        product.id,
                    'product_name':      product.name,
                    'category':          product.category,
                    'brand':             product.brand,
                    'unit_price':        product.unit_price,
                    'oct_predicted_qty': round(total_qty, 1),
                    'daily_forecasts':   [{'date': d, 'predicted_qty': round(q, 2)} for d, q in forecasts],
                    'rmse':              round(eval_obj.rmse, 4) if eval_obj else None,
                    'train_days':        train_result['train_days'] if train_result else None,
                })
            except ValueError as e:
                skipped.append(f"{product.name}: {e}")
            except Exception as e:
                skipped.append(f"{product.name}: {e}")

        results.sort(key=lambda x: x['oct_predicted_qty'], reverse=True)

        return Response({
            'model_type':          model_type,
            'trained_on':          'last 3 months',
            'forecast_month':      forecast_month_label or 'Next Month',
            'forecast_steps':      STEPS,
            'top_demand_products': results,
            'skipped':             skipped,
            'summary': {
                'total_products': len(products),
                'trained':        len(results),
                'skipped':        len(skipped),
            }
        })


class ForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response({'error': 'No shop linked to your account.'}, status=400)

        product_id = request.data.get('product_id')
        model_type = request.data.get('model_type', 'LSTM').upper()
        steps      = int(request.data.get('steps', 30))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)

        sales_qs = Sale.objects.filter(shop=shop, product_id=product_id)
        if not sales_qs.exists():
            return Response({'error': 'No sales data found for this product.'}, status=404)

        try:
            forecasts = forecast_future(
                sales_qs, shop.id, product_id, model_type,
                steps, str(settings.ML_MODELS_DIR)
            )
        except FileNotFoundError as e:
            return Response({'error': str(e)}, status=400)

        product = Product.objects.get(id=product_id)
        Forecast.objects.filter(shop=shop, product=product, model_type=model_type).delete()
        Forecast.objects.bulk_create([
            Forecast(shop=shop, product=product, model_type=model_type,
                     forecast_date=d, predicted_qty=q)
            for d, q in forecasts
        ])

        return Response({
            'forecasts': [{'date': d, 'predicted_qty': q} for d, q in forecasts]
        })
