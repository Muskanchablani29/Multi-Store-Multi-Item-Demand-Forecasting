from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=20, unique=True, null=True, blank=True, default=None)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    unit_price = models.FloatField(default=0)
    cost_price = models.FloatField(default=0)
    supplier_id = models.CharField(max_length=20, blank=True)
    supplier_name = models.CharField(max_length=100, blank=True)
    lead_time_days = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
