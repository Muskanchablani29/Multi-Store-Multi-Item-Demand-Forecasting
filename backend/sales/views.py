import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer
from shops.models import Shop
from products.models import Product

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('shop', 'product').all()
    serializer_class = SaleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        shop_id = self.request.query_params.get('shop_id')
        product_id = self.request.query_params.get('product_id')
        if shop_id:
            qs = qs.filter(shop_id=shop_id)
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = 0
        errors = []

        for i, row in enumerate(reader):
            try:
                shop, _ = Shop.objects.get_or_create(name=row['shop_name'].strip())
                product, _ = Product.objects.get_or_create(name=row['item_name'].strip())
                Sale.objects.create(
                    shop=shop,
                    product=product,
                    date=row['date'].strip(),
                    quantity=float(row['quantity'])
                )
                created += 1
            except Exception as e:
                errors.append(f"Row {i+2}: {str(e)}")

        return Response({'created': created, 'errors': errors}, status=status.HTTP_201_CREATED)
