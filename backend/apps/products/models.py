from django.db import models


class Product(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='BDT')
    stock_status = models.CharField(max_length=40, default='in_stock')
    category = models.CharField(max_length=120, blank=True)
    delivery_info = models.TextField(blank=True)
    return_policy = models.TextField(blank=True)
    warranty_info = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    embedding_status = models.CharField(max_length=20, default='pending')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
