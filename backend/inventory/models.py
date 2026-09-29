from django.db import models
from shops.models import Shop
from products.models import Product

class Inventory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory')
    current_stock = models.FloatField(default=0)
    reorder_point = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('shop', 'product')

    def __str__(self):
        return f"{self.shop} - {self.product}"
