from __future__ import annotations

from apps.businesses.models import Business
from apps.tenants.models import TeamMember


def get_user_business(user) -> Business | None:
    if not user or not user.is_authenticated:
        return None
    owned = Business.objects.filter(owner=user).first()
    if owned:
        return owned
    membership = TeamMember.objects.filter(user=user, is_active=True).select_related('business').first()
    return membership.business if membership else None


def get_user_role_for_business(user, business: Business | None) -> str | None:
    if not user or not user.is_authenticated or business is None:
        return None
    if business.owner_id == user.id:
        return "owner"
    membership = TeamMember.objects.filter(user=user, business=business, is_active=True).first()
    return membership.role if membership else None


def can_manage_business_data(user, business: Business | None) -> bool:
    role = get_user_role_for_business(user, business)
    return role in {"owner", "manager"}
