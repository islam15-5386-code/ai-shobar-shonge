from __future__ import annotations

from apps.businesses.access import get_user_business
from apps.tenants.models import TeamMember
from .models import Vendor, VendorStaff


def is_platform_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff))


def can_manage_marketplace(user, business) -> bool:
    if not user or not user.is_authenticated or not business:
        return False
    if business.owner_id == user.id:
        return True
    profile = getattr(user, "profile", None)
    if getattr(profile, "role", "") in ["owner", "manager"]:
        return True
    return TeamMember.objects.filter(user=user, business=business, is_active=True, role__in=['owner', 'manager']).exists()


def get_vendor_for_user(user, business=None):
    if not user or not user.is_authenticated:
        return None
    if business is None:
        business = get_user_business(user)
    if not business:
        return None
    owned = Vendor.objects.filter(business=business, owner_user=user, is_active=True).first()
    if owned:
        return owned
    membership = VendorStaff.objects.filter(user=user, vendor__business=business, is_active=True, vendor__is_active=True).select_related('vendor').first()
    return membership.vendor if membership else None


def can_access_vendor(user, vendor: Vendor) -> bool:
    if is_platform_admin(user):
        return True
    if vendor.business.owner_id == user.id:
        return True
    if TeamMember.objects.filter(user=user, business=vendor.business, is_active=True, role__in=['owner', 'manager']).exists():
        return True
    if vendor.owner_user_id == user.id:
        return True
    return VendorStaff.objects.filter(user=user, vendor=vendor, is_active=True).exists()
