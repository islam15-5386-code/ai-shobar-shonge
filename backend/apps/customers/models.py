from django.db import models


class CustomerProfile(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='customers')
    vendor = models.ForeignKey('marketplace.Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    last_order = models.ForeignKey('marketplace.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_customers')
    last_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_customers')
    external_source = models.CharField(max_length=32, default='facebook')
    external_id = models.CharField(max_length=128)
    name = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'external_source', 'external_id')
