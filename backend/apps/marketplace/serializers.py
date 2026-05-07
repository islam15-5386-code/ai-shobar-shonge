from rest_framework import serializers
from .models import Vendor, VendorStaff, MarketplaceCategory, Order, OrderItem, VendorCommission, VendorPayout


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['id', 'business', 'created_at', 'updated_at']


class VendorStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorStaff
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MarketplaceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceCategory
        fields = '__all__'
        read_only_fields = ['id', 'business']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'business', 'order_number', 'created_at', 'updated_at']


class VendorCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCommission
        fields = '__all__'


class VendorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPayout
        fields = '__all__'
        read_only_fields = ['id', 'business', 'requested_at', 'paid_at']
