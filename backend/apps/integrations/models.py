from django.db import models


class MessengerIntegration(models.Model):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='messenger_integration')
    page_id = models.CharField(max_length=128, unique=True)
    page_access_token = models.CharField(max_length=500)
    app_id = models.CharField(max_length=128, blank=True)
    app_secret = models.CharField(max_length=255, blank=True)
    verify_token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WhatsAppIntegration(models.Model):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='whatsapp_integration')
    phone_number_id = models.CharField(max_length=128, unique=True)
    access_token = models.CharField(max_length=500)
    verify_token = models.CharField(max_length=255)
    waba_id = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
