from __future__ import annotations

from apps.businesses.models import Business
from apps.tenants.models import TeamMember
from apps.marketplace.models import VendorStaff


def get_user_business(user) -> Business | None:
    if not user or not user.is_authenticated:
        return None
    owned = Business.objects.filter(owner=user).first()
    if owned:
        return owned
    membership = TeamMember.objects.filter(user=user, is_active=True).select_related('business').first()
    if membership:
        return membership.business
    vendor_membership = (
        VendorStaff.objects.filter(user=user, is_active=True, vendor__is_active=True)
        .select_related('vendor__business')
        .first()
    )
    return vendor_membership.vendor.business if vendor_membership else None


def get_user_role_for_business(user, business: Business | None) -> str | None:
    if not user or not user.is_authenticated or business is None:
        return None
    if business.owner_id == user.id:
        return "owner"
    membership = TeamMember.objects.filter(user=user, business=business, is_active=True).first()
    return membership.role if membership else None


<<<<<<< HEAD
def is_super_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff))


def is_business_owner(user, business: Business | None) -> bool:
    return bool(user and business and business.owner_id == user.id)


def is_manager(user, business: Business | None) -> bool:
    return get_user_role_for_business(user, business) == "manager"


def is_owner_or_manager(user, business: Business | None) -> bool:
    return is_business_owner(user, business) or is_manager(user, business)


def is_agent(user, business: Business | None) -> bool:
    return get_user_role_for_business(user, business) == "agent"


def get_vendor_staff_role(user, business: Business | None) -> str | None:
    if not user or not user.is_authenticated or not business:
        return None
    membership = (
        VendorStaff.objects.filter(user=user, vendor__business=business, is_active=True, vendor__is_active=True)
        .select_related('vendor')
        .first()
    )
    return membership.role if membership else None


def can_manage_billing(user, business: Business | None) -> bool:
    return is_super_admin(user) or is_business_owner(user, business)


def can_manage_integrations(user, business: Business | None) -> bool:
    return is_super_admin(user) or is_business_owner(user, business)


def can_view_analytics(user, business: Business | None) -> bool:
    return is_super_admin(user) or is_owner_or_manager(user, business)


def can_manage_business_profile(user, business: Business | None) -> bool:
    return is_super_admin(user) or is_owner_or_manager(user, business)


def can_manage_team(user, business: Business | None) -> bool:
    return is_super_admin(user) or is_owner_or_manager(user, business)


def can_manage_business_data(user, business: Business | None) -> bool:
    role = get_user_role_for_business(user, business)
    return is_super_admin(user) or role in {"owner", "manager"}
=======
def can_manage_business_data(user, business: Business | None) -> bool:
    role = get_user_role_for_business(user, business)
    return role in {"owner", "manager"}
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
