from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Inventory
from .serializers import InventorySerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('shop', 'product').all()
    serializer_class = InventorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        return qs

    @action(detail=False, methods=['get'], url_path='reorder-alerts')
    def reorder_alerts(self, request):
        alerts = Inventory.objects.select_related('shop', 'product').filter(
            current_stock__lte=F('reorder_point')
        )
        serializer = InventorySerializer(alerts, many=True)
        return Response(serializer.data)
