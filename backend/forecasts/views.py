from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Forecast, ModelEvaluation
from .serializers import ForecastSerializer, ModelEvaluationSerializer


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class ForecastViewSet(viewsets.ModelViewSet):
    serializer_class = ForecastSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shop = _get_shop(self.request.user)
        if not shop:
            return Forecast.objects.none()
        qs = Forecast.objects.select_related('shop', 'product').filter(shop=shop)
        product_id = self.request.query_params.get('product_id')
        model_type = self.request.query_params.get('model_type')
        if product_id:
            qs = qs.filter(product_id=product_id)
        if model_type:
            qs = qs.filter(model_type=model_type)
        return qs


class ModelEvaluationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ModelEvaluationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shop = _get_shop(self.request.user)
        if not shop:
            return ModelEvaluation.objects.none()
        qs = ModelEvaluation.objects.select_related('shop', 'product').filter(shop=shop)
        product_id = self.request.query_params.get('product_id')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs
