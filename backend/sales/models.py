from django.db import models
from shops.models import Shop
from products.models import Product

class Sale(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField()
    quantity = models.FloatField()
    unit_price = models.FloatField(default=0)
    cost_price = models.FloatField(default=0)
    discount_percent = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)
    total_sales = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    promotion = models.BooleanField(default=False)
    promotion_type = models.CharField(max_length=50, blank=True, default='No Promotion')
    promotion_discount = models.FloatField(default=0)
    is_holiday = models.BooleanField(default=False)
    holiday_name = models.CharField(max_length=100, blank=True)
    season = models.CharField(max_length=50, blank=True)
    day_of_week = models.IntegerField(default=0)
    is_weekend = models.BooleanField(default=False)
    month = models.IntegerField(default=1)
    week_number = models.IntegerField(default=1)

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['shop', 'product', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['shop']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.shop} - {self.product} - {self.date}"
