from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Vendor(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    )

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vendors')
    owner_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_vendors')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    logo = models.URLField(blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=120, blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    commission_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    payout_method = models.CharField(max_length=80, blank=True)
    bank_account_info = models.JSONField(default=dict, blank=True)
    business_hours = models.CharField(max_length=120, blank=True)
    return_policy = models.TextField(blank=True)
    delivery_policy = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'slug')


class VendorStaff(models.Model):
    ROLE_CHOICES = (
        ('vendor_owner', 'Vendor Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='staff_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_staff_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'user')


class MarketplaceCategory(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='marketplace_categories')
    name = models.CharField(max_length=120)
    slug = models.SlugField()
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('business', 'slug')


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='marketplace_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey('customers.CustomerProfile', on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='BDT')
    delivery_address = models.TextField(blank=True)
    customer_phone = models.CharField(max_length=40, blank=True)
    customer_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business', 'order_number')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='order_items')
    product_name_snapshot = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)


class VendorCommission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
    )
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vendor_commissions')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='commissions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='commissions')
    commission_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vendor_earning = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class VendorPayout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='vendor_payouts')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout_method = models.CharField(max_length=80, blank=True)
    transaction_reference = models.CharField(max_length=120, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)


class MarketplaceSetting(models.Model):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='marketplace_settings')
    default_commission_rate = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('10.00'))
    auto_approve_vendors = models.BooleanField(default=False)
    auto_approve_products = models.BooleanField(default=False)
    vendor_self_signup_enabled = models.BooleanField(default=False)
    require_vendor_kyc = models.BooleanField(default=False)
    min_payout_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('1000.00'))
    default_payout_method = models.CharField(max_length=80, default='bank')
    default_return_policy = models.TextField(blank=True)
    default_delivery_policy = models.TextField(blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=40, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
