from django.conf import settings
from django.db import models


class Business(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='business')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    website = models.URLField(blank=True)
    welcome_message = models.TextField(default='Hello! How can I help you today?')
    handover_enabled = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True, default='shop')
    support_email = models.EmailField(blank=True, default='')
    support_phone = models.CharField(max_length=32, blank=True, default='')
    business_hours = models.CharField(max_length=120, blank=True, default='')
    address = models.TextField(blank=True, default='')
    logo = models.ImageField(upload_to='business_logos/', blank=True, null=True)
    logo_extracted_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
