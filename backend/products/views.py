from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer


def _get_shop(user):
    try:
        return user.shop
    except Exception:
        return None


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        shop = _get_shop(self.request.user)
        if not shop:
            return Product.objects.none()
        qs = Product.objects.filter(shop=shop)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs
