from django.db import models
from shops.models import Shop
from products.models import Product

class Sale(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField()
    quantity = models.FloatField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.shop} - {self.product} - {self.date}"
