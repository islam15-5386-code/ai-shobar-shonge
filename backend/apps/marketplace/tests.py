from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import UserProfile
from apps.billing.models import PricingPlan, Subscription
from apps.businesses.models import Business
from apps.marketplace.models import Vendor, Order, VendorCommission
from apps.products.models import Product


class MarketplaceTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner@test.com', password='pass123')
        UserProfile.objects.create(user=self.owner, full_name='Owner', role='owner')
        self.business = Business.objects.create(owner=self.owner, name='Biz', slug='biz')
        plan = PricingPlan.objects.create(code='p1', name='Plan', monthly_price=10, message_limit=1000, seat_limit=5, vendor_limit=1, product_limit_per_vendor=10, order_limit=1000, agent_limit=5, ai_reply_limit=1000)
        Subscription.objects.create(business=self.business, plan=plan, status='active')
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)

    def test_marketplace_owner_create_vendor(self):
        r = self.client.post('/api/vendors/', {'name': 'Vendor One', 'slug': 'vendor-one'}, format='json')
        self.assertEqual(r.status_code, 201)

    def test_vendor_limit_blocks_extra_vendor(self):
        self.client.post('/api/vendors/', {'name': 'Vendor One', 'slug': 'vendor-one'}, format='json')
        r = self.client.post('/api/vendors/', {'name': 'Vendor Two', 'slug': 'vendor-two'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_storefront_order_creates_commission(self):
        v = Vendor.objects.create(business=self.business, owner_user=self.owner, name='V1', slug='v1', status='approved', is_active=True, commission_rate=Decimal('10'))
        p = Product.objects.create(business=self.business, vendor=v, name='P1', slug='p1', price=Decimal('100'), stock_quantity=5, approval_status='approved', is_active=True)
        r = self.client.post('/api/storefront/orders/', {
            'business_id': self.business.id,
            'vendor_id': v.id,
            'customer': {'name': 'Rahim', 'phone': '+8801711111111'},
            'items': [{'product_id': p.id, 'quantity': 1}],
            'delivery_address': 'Dhaka'
        }, format='json')
        self.assertEqual(r.status_code, 201)
        order = Order.objects.get(id=r.data['order_id'])
        self.assertTrue(VendorCommission.objects.filter(order=order).exists())
