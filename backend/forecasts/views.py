from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Forecast, ModelEvaluation
from .serializers import ForecastSerializer, ModelEvaluationSerializer

class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.select_related('shop', 'product').all()
    serializer_class = ForecastSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        shop_id = self.request.query_params.get('shop_id')
        product_id = self.request.query_params.get('product_id')
        model_type = self.request.query_params.get('model_type')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        if model_type:
            qs = qs.filter(model_type=model_type)
        return qs

class ModelEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModelEvaluation.objects.select_related('shop', 'product').all()
    serializer_class = ModelEvaluationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        shop_id = self.request.query_params.get('shop_id')
        product_id = self.request.query_params.get('product_id')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs
