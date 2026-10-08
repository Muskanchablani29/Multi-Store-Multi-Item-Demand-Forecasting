from django.db import models
from django.contrib.auth.models import User


class Shop(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop', null=True, blank=True)
    shop_id = models.CharField(max_length=20, unique=True, null=True, blank=True, default=None)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True, default='Footwear')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
