from django.db.models import F, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Inventory
from .serializers import InventorySerializer
from forecasts.models import Forecast


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shop = _get_shop(self.request.user)
        if not shop:
            return Inventory.objects.none()
        return Inventory.objects.select_related('shop', 'product').filter(shop=shop)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'shop_id' in data and 'shop' not in data:
            data['shop'] = data.pop('shop_id')
        if 'product_id' in data and 'product' not in data:
            data['product'] = data.pop('product_id')

        shop_pk    = data.get('shop')
        product_pk = data.get('product')
        existing   = Inventory.objects.filter(shop_id=shop_pk, product_id=product_pk).first()
        if existing:
            serializer = self.get_serializer(existing, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='reorder-alerts')
    def reorder_alerts(self, request):
        shop = _get_shop(request.user)
        if not shop:
            return Response([])
        alerts = (Inventory.objects
                  .select_related('shop', 'product')
                  .filter(shop=shop, current_stock__lte=F('reorder_point')))
        return Response(InventorySerializer(alerts, many=True).data)

    @action(detail=False, methods=['get'], url_path='recommendation')
    def recommendation(self, request):
        shop = _get_shop(request.user)
        product_id = request.query_params.get('product_id')
        model_type = request.query_params.get('model_type', 'LSTM').upper()

        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)

        try:
            inv = Inventory.objects.get(shop=shop, product_id=product_id)
        except Inventory.DoesNotExist:
            return Response({'error': 'Inventory record not found'}, status=404)

        forecasts        = Forecast.objects.filter(shop=shop, product_id=product_id, model_type=model_type)
        predicted_demand = forecasts.aggregate(s=Sum('predicted_qty'))['s'] or 0
        forecast_days    = forecasts.count() or 1
        daily_demand     = predicted_demand / forecast_days
        lead_demand      = daily_demand * inv.lead_time_days
        reorder_qty      = max(0, lead_demand + inv.safety_stock - inv.current_stock)

        if inv.current_stock <= 0:
            inv_status = 'Out of Stock'
        elif inv.current_stock <= inv.safety_stock:
            inv_status = 'Reorder Required'
        elif inv.current_stock <= inv.reorder_point:
            inv_status = 'Low Stock'
        else:
            inv_status = 'Sufficient Stock'

        return Response({
            'shop':                  inv.shop.name,
            'product':               inv.product.name,
            'category':              inv.product.category,
            'current_stock':         inv.current_stock,
            'safety_stock':          inv.safety_stock,
            'reorder_point':         inv.reorder_point,
            'lead_time_days':        inv.lead_time_days,
            'predicted_demand':      round(predicted_demand, 2),
            'daily_demand':          round(daily_demand, 2),
            'recommended_order_qty': round(reorder_qty, 0),
            'inventory_status':      inv_status,
        })
