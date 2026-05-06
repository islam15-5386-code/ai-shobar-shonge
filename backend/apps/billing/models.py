from django.db import models


class PricingPlan(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    message_limit = models.IntegerField(default=500)
    seat_limit = models.IntegerField(default=1)
    features = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Subscription(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('trial', 'Trial'),
    )

    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(PricingPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    start_date = models.DateTimeField(auto_now_add=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UsageRecord(models.Model):
    PERIOD_CHOICES = (
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
    )
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='usage_records')
    metric = models.CharField(max_length=60, default='messages')
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    period_key = models.CharField(max_length=20)  # e.g. 2026-05
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'metric', 'period_type', 'period_key')


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('paid', 'Paid'),
        ('void', 'Void'),
    )
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    invoice_number = models.CharField(max_length=40, unique=True)
    due_date = models.DateField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
