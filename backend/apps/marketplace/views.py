from __future__ import annotations

import csv
import io
import uuid
from decimal import Decimal

from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.businesses.access import get_user_business
from apps.conversations.models import Conversation, Message
from apps.customers.models import CustomerProfile
from apps.faqs.models import FAQ
from apps.products.models import Product
from apps.tickets.models import Ticket
from .models import MarketplaceCategory, MarketplaceSetting, Order, OrderItem, Vendor, VendorCommission, VendorPayout, VendorStaff
from .permissions import can_access_vendor, can_manage_marketplace, get_vendor_for_user
from .serializers import (
    MarketplaceCategorySerializer,
    OrderSerializer,
    VendorCommissionSerializer,
    VendorPayoutSerializer,
    VendorSerializer,
)


def _plan_features(business):
    sub = getattr(business, "subscription", None)
    return (sub.plan.features or {}) if sub and sub.plan else {}


def _vendor_limit_ok(business) -> bool:
    sub = getattr(business, "subscription", None)
    features = _plan_features(business)
    limit = int(features.get("vendor_limit", getattr(sub.plan, "vendor_limit", 999999) if sub else 999999))
    return Vendor.objects.filter(business=business, is_active=True).count() < limit


def _product_limit_ok(business, vendor) -> bool:
    sub = getattr(business, "subscription", None)
    features = _plan_features(business)
    per_vendor = int(
        features.get(
            "product_limit_per_vendor",
            getattr(sub.plan, "product_limit_per_vendor", 999999) if sub else 999999,
        )
    )
    return Product.objects.filter(business=business, vendor=vendor, is_active=True).count() < per_vendor


def _get_marketplace_settings(business):
    settings_obj, _ = MarketplaceSetting.objects.get_or_create(business=business)
    return settings_obj


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vendors(request):
    business = get_user_business(request.user)
    if not business:
        return Response({"detail": "business setup required"}, status=400)

    if request.method == "GET":
        qs = Vendor.objects.filter(business=business).order_by("-created_at")
        if not can_manage_marketplace(request.user, business):
            vendor = get_vendor_for_user(request.user, business)
            qs = qs.filter(id=vendor.id) if vendor else qs.none()
        if request.query_params.get("status"):
            qs = qs.filter(status=request.query_params.get("status"))
        if request.query_params.get("city"):
            qs = qs.filter(city__icontains=request.query_params.get("city"))
        if request.query_params.get("category"):
            qs = qs.filter(category__icontains=request.query_params.get("category"))
        if request.query_params.get("search"):
            s = request.query_params.get("search")
            qs = qs.filter(name__icontains=s)
        return Response(VendorSerializer(qs, many=True).data)

    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    if not _vendor_limit_ok(business):
        return Response({"detail": "vendor limit exceeded for current plan"}, status=400)

    data = request.data.copy()
    settings_obj = _get_marketplace_settings(business)
    if not data.get("slug") and data.get("name"):
        data["slug"] = slugify(str(data.get("name")))
    if not data.get("commission_rate"):
        data["commission_rate"] = str(settings_obj.default_commission_rate)
    if not data.get("payout_method"):
        data["payout_method"] = settings_obj.default_payout_method
    if not data.get("return_policy"):
        data["return_policy"] = settings_obj.default_return_policy
    if not data.get("delivery_policy"):
        data["delivery_policy"] = settings_obj.default_delivery_policy
    if "status" not in data:
        data["status"] = "approved" if settings_obj.auto_approve_vendors else "pending"
    serializer = VendorSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    owner_user = request.user
    vendor = serializer.save(business=business, owner_user=owner_user)
    VendorStaff.objects.update_or_create(vendor=vendor, user=owner_user, defaults={"role": "vendor_owner", "is_active": True})
    return Response(VendorSerializer(vendor).data, status=201)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def vendor_detail(request, vendor_id):
    business = get_user_business(request.user)
    vendor = Vendor.objects.filter(id=vendor_id, business=business).first()
    if not vendor:
        return Response({"detail": "vendor not found"}, status=404)
    if not can_access_vendor(request.user, vendor):
        return Response({"detail": "permission denied"}, status=403)

    if request.method == "GET":
        return Response(VendorSerializer(vendor).data)

    if not can_manage_marketplace(request.user, business) and vendor.owner_user_id != request.user.id:
        return Response({"detail": "permission denied"}, status=403)
    serializer = VendorSerializer(vendor, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def _vendor_status_action(request, vendor_id, next_status):
    business = get_user_business(request.user)
    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    vendor = Vendor.objects.filter(id=vendor_id, business=business).first()
    if not vendor:
        return Response({"detail": "vendor not found"}, status=404)
    vendor.status = next_status
    vendor.is_active = next_status in ["approved", "pending"]
    vendor.save(update_fields=["status", "is_active", "updated_at"])
    return Response({"id": vendor.id, "status": vendor.status, "is_active": vendor.is_active})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_approve(request, vendor_id):
    return _vendor_status_action(request, vendor_id, "approved")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_reject(request, vendor_id):
    return _vendor_status_action(request, vendor_id, "rejected")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_suspend(request, vendor_id):
    return _vendor_status_action(request, vendor_id, "suspended")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_activate(request, vendor_id):
    return _vendor_status_action(request, vendor_id, "approved")


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def vendor_commission(request, vendor_id):
    business = get_user_business(request.user)
    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    vendor = Vendor.objects.filter(id=vendor_id, business=business).first()
    if not vendor:
        return Response({"detail": "vendor not found"}, status=404)
    vendor.commission_rate = Decimal(str(request.data.get("commission_rate", vendor.commission_rate)))
    vendor.save(update_fields=["commission_rate", "updated_at"])
    return Response({"id": vendor.id, "commission_rate": str(vendor.commission_rate)})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def marketplace_settings(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)

    settings_obj = _get_marketplace_settings(business)
    if request.method == "GET":
        return Response(
            {
                "id": settings_obj.id,
                "default_commission_rate": str(settings_obj.default_commission_rate),
                "auto_approve_vendors": settings_obj.auto_approve_vendors,
                "auto_approve_products": settings_obj.auto_approve_products,
                "vendor_self_signup_enabled": settings_obj.vendor_self_signup_enabled,
                "require_vendor_kyc": settings_obj.require_vendor_kyc,
                "min_payout_amount": str(settings_obj.min_payout_amount),
                "default_payout_method": settings_obj.default_payout_method,
                "default_return_policy": settings_obj.default_return_policy,
                "default_delivery_policy": settings_obj.default_delivery_policy,
                "support_email": settings_obj.support_email,
                "support_phone": settings_obj.support_phone,
            }
        )

    if "default_commission_rate" in request.data:
        settings_obj.default_commission_rate = Decimal(str(request.data.get("default_commission_rate", settings_obj.default_commission_rate)))
    if "auto_approve_vendors" in request.data:
        settings_obj.auto_approve_vendors = bool(request.data.get("auto_approve_vendors"))
    if "auto_approve_products" in request.data:
        settings_obj.auto_approve_products = bool(request.data.get("auto_approve_products"))
    if "vendor_self_signup_enabled" in request.data:
        settings_obj.vendor_self_signup_enabled = bool(request.data.get("vendor_self_signup_enabled"))
    if "require_vendor_kyc" in request.data:
        settings_obj.require_vendor_kyc = bool(request.data.get("require_vendor_kyc"))
    if "min_payout_amount" in request.data:
        settings_obj.min_payout_amount = Decimal(str(request.data.get("min_payout_amount", settings_obj.min_payout_amount)))
    if "default_payout_method" in request.data:
        settings_obj.default_payout_method = str(request.data.get("default_payout_method") or "bank").strip() or "bank"
    if "default_return_policy" in request.data:
        settings_obj.default_return_policy = str(request.data.get("default_return_policy") or "")
    if "default_delivery_policy" in request.data:
        settings_obj.default_delivery_policy = str(request.data.get("default_delivery_policy") or "")
    if "support_email" in request.data:
        settings_obj.support_email = str(request.data.get("support_email") or "")
    if "support_phone" in request.data:
        settings_obj.support_phone = str(request.data.get("support_phone") or "")
    settings_obj.save()
    return Response({"detail": "saved"})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def marketplace_categories(request):
    business = get_user_business(request.user)
    if not business:
        return Response({"detail": "business setup required"}, status=400)
    if request.method == "GET":
        qs = MarketplaceCategory.objects.filter(business=business).order_by("name")
        return Response(MarketplaceCategorySerializer(qs, many=True).data)
    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    data = request.data.copy()
    if not data.get("slug") and data.get("name"):
        data["slug"] = slugify(str(data.get("name")))
    s = MarketplaceCategorySerializer(data=data)
    s.is_valid(raise_exception=True)
    s.save(business=business)
    return Response(s.data, status=201)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def marketplace_category_detail(request, category_id):
    business = get_user_business(request.user)
    category = MarketplaceCategory.objects.filter(id=category_id, business=business).first()
    if not category:
        return Response({"detail": "category not found"}, status=404)
    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    if request.method == "PATCH":
        s = MarketplaceCategorySerializer(category, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)
    category.delete()
    return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_products(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    qs = Product.objects.filter(business=business).select_related("vendor").order_by("-created_at")
    if request.query_params.get("vendor"):
        qs = qs.filter(vendor_id=request.query_params.get("vendor"))
    if request.query_params.get("status"):
        qs = qs.filter(approval_status=request.query_params.get("status"))
    if request.query_params.get("category"):
        qs = qs.filter(category__icontains=request.query_params.get("category"))
    payload = []
    for p in qs:
        payload.append(
            {
                "id": p.id,
                "name": p.name,
                "vendor_id": p.vendor_id,
                "vendor_name": p.vendor.name if p.vendor else "",
                "price": str(p.price),
                "approval_status": p.approval_status,
                "is_active": p.is_active,
                "category": p.category,
            }
        )
    return Response(payload)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def marketplace_product_approve(request, product_id):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    p = Product.objects.filter(id=product_id, business=business).first()
    if not p:
        return Response({"detail": "product not found"}, status=404)
    p.approval_status = "approved"
    p.save(update_fields=["approval_status"])
    return Response({"id": p.id, "approval_status": p.approval_status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def marketplace_product_reject(request, product_id):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    p = Product.objects.filter(id=product_id, business=business).first()
    if not p:
        return Response({"detail": "product not found"}, status=404)
    p.approval_status = "rejected"
    p.save(update_fields=["approval_status"])
    return Response({"id": p.id, "approval_status": p.approval_status})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_orders(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    qs = Order.objects.filter(business=business).select_related("vendor", "customer").order_by("-created_at")
    if request.query_params.get("vendor"):
        qs = qs.filter(vendor_id=request.query_params.get("vendor"))
    if request.query_params.get("status"):
        qs = qs.filter(status=request.query_params.get("status"))
    if request.query_params.get("payment"):
        qs = qs.filter(payment_status=request.query_params.get("payment"))
    return Response(OrderSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_order_detail(request, order_id):
    business = get_user_business(request.user)
    order = Order.objects.filter(id=order_id, business=business).first()
    if not order:
        return Response({"detail": "order not found"}, status=404)
    if not can_manage_marketplace(request.user, business) and not can_access_vendor(request.user, order.vendor):
        return Response({"detail": "permission denied"}, status=403)
    return Response(OrderSerializer(order).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def marketplace_order_status(request, order_id):
    business = get_user_business(request.user)
    order = Order.objects.filter(id=order_id, business=business).first()
    if not order:
        return Response({"detail": "order not found"}, status=404)
    if not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    val = str(request.data.get("status", "")).strip()
    if val not in dict(Order.STATUS_CHOICES):
        return Response({"detail": "invalid status"}, status=400)
    order.status = val
    order.save(update_fields=["status", "updated_at"])
    return Response({"id": order.id, "status": order.status})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_orders_export(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["order_number", "vendor", "status", "payment_status", "total", "created_at"])
    for o in Order.objects.filter(business=business).select_related("vendor"):
        writer.writerow([o.order_number, o.vendor.name, o.status, o.payment_status, str(o.total), o.created_at.isoformat()])
    resp = HttpResponse(output.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = "attachment; filename=marketplace_orders.csv"
    return resp


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def marketplace_orders_demo_create(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)

    vendor = Vendor.objects.filter(business=business, is_active=True).order_by("id").first()
    if not vendor:
        return Response({"detail": "no active vendor found"}, status=400)

    product = Product.objects.filter(business=business, vendor=vendor, is_active=True).order_by("id").first()
    if not product:
        product = Product.objects.filter(business=business, is_active=True).order_by("id").first()
    if not product:
        product = Product.objects.create(
            business=business,
            vendor=vendor,
            name="Demo Product",
            slug=f"demo-product-{uuid.uuid4().hex[:6]}",
            description="Auto-created demo product for marketplace order testing",
            price=Decimal("500"),
            currency="BDT",
            stock_status="in_stock",
            is_active=True,
        )

    external_id = f"demo-cust-{uuid.uuid4().hex[:8]}"
    customer = CustomerProfile.objects.create(
        business=business,
        vendor=vendor,
        external_source="manual",
        external_id=external_id,
        name=str(request.data.get("customer_name", "Demo Customer")),
        metadata={"phone": str(request.data.get("customer_phone", "+8801700000000"))},
    )

    qty = int(request.data.get("quantity", 1) or 1)
    subtotal = Decimal(product.price) * qty
    delivery_fee = Decimal(str(request.data.get("delivery_fee", "80")))
    total = subtotal + delivery_fee
    order_no = f"ORD-{business.id}-{uuid.uuid4().hex[:8].upper()}"
    order = Order.objects.create(
        business=business,
        vendor=vendor,
        customer=customer,
        order_number=order_no,
        status="pending",
        payment_status="unpaid",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        discount=Decimal("0"),
        total=total,
        currency="BDT",
        delivery_address=str(request.data.get("delivery_address", "Dhaka")),
        customer_phone=customer.metadata.get("phone", ""),
        customer_email="",
        notes="Demo order from marketplace orders page",
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        vendor=vendor,
        product_name_snapshot=product.name,
        unit_price=product.price,
        quantity=qty,
        total_price=subtotal,
    )

    return Response({"id": order.id, "order_number": order.order_number, "status": order.status}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_commissions(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    qs = VendorCommission.objects.filter(business=business).select_related("vendor", "order").order_by("-created_at")
    return Response(VendorCommissionSerializer(qs, many=True).data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def marketplace_payouts(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    if request.method == "GET":
        qs = VendorPayout.objects.filter(business=business).select_related("vendor").order_by("-requested_at")
        return Response(VendorPayoutSerializer(qs, many=True).data)

    vendor_id = request.data.get("vendor_id")
    vendor = Vendor.objects.filter(id=vendor_id, business=business).first()
    if not vendor:
        return Response({"detail": "vendor not found"}, status=404)
    settings_obj = _get_marketplace_settings(business)
    amount = Decimal(str(request.data.get("amount", "0")))
    if amount < settings_obj.min_payout_amount:
        return Response({"detail": f"minimum payout amount is {settings_obj.min_payout_amount}"}, status=400)
    payout = VendorPayout.objects.create(
        business=business,
        vendor=vendor,
        amount=amount,
        status="pending",
        payout_method=str(request.data.get("payout_method", vendor.payout_method or settings_obj.default_payout_method or "bank")),
        transaction_reference=str(request.data.get("transaction_reference", "")),
    )
    return Response(VendorPayoutSerializer(payout).data, status=201)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def marketplace_payout_mark_paid(request, payout_id):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    payout = VendorPayout.objects.filter(id=payout_id, business=business).first()
    if not payout:
        return Response({"detail": "payout not found"}, status=404)
    payout.status = "paid"
    payout.paid_at = timezone.now()
    payout.transaction_reference = str(request.data.get("transaction_reference", payout.transaction_reference))
    payout.save(update_fields=["status", "paid_at", "transaction_reference"])
    VendorCommission.objects.filter(business=business, vendor=payout.vendor, status="confirmed").update(status="paid")
    return Response(VendorPayoutSerializer(payout).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_payouts_export(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["vendor", "amount", "status", "requested_at", "paid_at"])
    for p in VendorPayout.objects.filter(business=business).select_related("vendor"):
        writer.writerow([p.vendor.name, str(p.amount), p.status, p.requested_at.isoformat(), p.paid_at.isoformat() if p.paid_at else ""])
    resp = HttpResponse(output.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = "attachment; filename=vendor_payouts.csv"
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_analytics_overview(request):
    business = get_user_business(request.user)
    if not business or not can_manage_marketplace(request.user, business):
        return Response({"detail": "permission denied"}, status=403)

    total_orders = Order.objects.filter(business=business).count()
    complaint_tickets = Ticket.objects.filter(business=business, subject__icontains="complaint").count()
    top_vendors = list(
        Vendor.objects.filter(business=business).annotate(order_count=Count("orders")).order_by("-order_count").values("id", "name", "order_count")[:5]
    )
    top_products = list(
        Product.objects.filter(business=business)
        .annotate(order_count=Count("order_items"))
        .order_by("-order_count")
        .values("id", "name", "order_count")[:5]
    )

    return Response(
        {
            "total_vendors": Vendor.objects.filter(business=business).count(),
            "active_vendors": Vendor.objects.filter(business=business, is_active=True).count(),
            "pending_vendor_approvals": Vendor.objects.filter(business=business, status="pending").count(),
            "total_marketplace_orders": total_orders,
            "total_sales": str(Order.objects.filter(business=business).aggregate(v=Sum("total"))["v"] or Decimal("0")),
            "total_commission": str(
                VendorCommission.objects.filter(business=business).aggregate(v=Sum("commission_amount"))["v"] or Decimal("0")
            ),
            "pending_payouts": VendorPayout.objects.filter(business=business, status__in=["pending", "processing"]).count(),
            "top_vendors": top_vendors,
            "top_products": top_products,
            "vendor_ticket_count": Ticket.objects.filter(business=business, vendor__isnull=False).count(),
            "order_complaint_rate": round((complaint_tickets / total_orders) * 100, 2) if total_orders else 0,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def marketplace_analytics_export(request):
    data = marketplace_analytics_overview(request).data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for k, v in data.items():
        if isinstance(v, (list, dict)):
            continue
        writer.writerow([k, v])
    resp = HttpResponse(output.getvalue(), content_type="text/csv")
    resp["Content-Disposition"] = "attachment; filename=marketplace_analytics.csv"
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_dashboard(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    if not vendor:
        return Response({"detail": "vendor access not found"}, status=403)
    orders = Order.objects.filter(business=business, vendor=vendor)
    open_tickets = Ticket.objects.filter(business=business, vendor=vendor, status__in=["open", "in_progress"]).count()
    return Response(
        {
            "total_orders": orders.count(),
            "pending_orders": orders.filter(status="pending").count(),
            "delivered_orders": orders.filter(status="delivered").count(),
            "total_sales": str(orders.aggregate(v=Sum("total"))["v"] or Decimal("0")),
            "vendor_earnings": str(
                VendorCommission.objects.filter(business=business, vendor=vendor).aggregate(v=Sum("vendor_earning"))["v"] or Decimal("0")
            ),
            "open_tickets": open_tickets,
            "top_products": list(
                Product.objects.filter(business=business, vendor=vendor)
                .annotate(order_count=Count("order_items"))
                .order_by("-order_count")
                .values("id", "name", "order_count")[:5]
            ),
            "recent_orders": OrderSerializer(orders.order_by("-created_at")[:10], many=True).data,
            "recent_customer_messages": [
                {"conversation_id": m.conversation_id, "text": m.text, "created_at": m.created_at}
                for m in Message.objects.filter(conversation__business=business, conversation__vendor=vendor).order_by("-created_at")[:10]
            ],
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vendor_products(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    if not vendor:
        return Response({"detail": "vendor access not found"}, status=403)

    if request.method == "GET":
        qs = Product.objects.filter(business=business, vendor=vendor).order_by("-created_at")
        return Response(
            [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": str(p.price),
                    "stock_quantity": p.stock_quantity,
                    "approval_status": p.approval_status,
                    "is_active": p.is_active,
                    "category": p.category,
                }
                for p in qs
            ]
        )

    if not _product_limit_ok(business, vendor):
        return Response({"detail": "product limit exceeded for current plan"}, status=400)
    data = request.data
    p = Product.objects.create(
        business=business,
        vendor=vendor,
        name=str(data.get("name", "")).strip(),
        slug=slugify(str(data.get("slug") or data.get("name") or uuid.uuid4().hex[:8])),
        description=str(data.get("description", "")),
        price=Decimal(str(data.get("price", "0"))),
        sale_price=Decimal(str(data.get("sale_price", "0") or "0")),
        currency=str(data.get("currency", "BDT")),
        stock_quantity=int(data.get("stock_quantity", 0)),
        stock_status=str(data.get("stock_status", "in_stock")),
        sku=str(data.get("sku", "")),
        image_url=str(data.get("image_url", "")),
        gallery=data.get("gallery") or [],
        delivery_info=str(data.get("delivery_info", "")),
        return_policy=str(data.get("return_policy", "")),
        warranty_info=str(data.get("warranty_info", "")),
        category=str(data.get("category", "")),
        approval_status="draft",
        embedding_status="pending",
        is_active=bool(data.get("is_active", True)),
    )
    return Response({"id": p.id, "name": p.name, "approval_status": p.approval_status}, status=201)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def vendor_product_detail(request, product_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    p = Product.objects.filter(id=product_id, business=business, vendor=vendor).first()
    if not p:
        return Response({"detail": "product not found"}, status=404)
    if request.method == "GET":
        return Response({"id": p.id, "name": p.name, "description": p.description, "price": str(p.price), "approval_status": p.approval_status})
    if request.method == "PATCH":
        for fld in ["name", "description", "stock_status", "category", "delivery_info", "return_policy", "warranty_info", "sku", "image_url"]:
            if fld in request.data:
                setattr(p, fld, request.data.get(fld))
        if "price" in request.data:
            p.price = Decimal(str(request.data.get("price")))
        if "sale_price" in request.data:
            p.sale_price = Decimal(str(request.data.get("sale_price") or "0"))
        if "stock_quantity" in request.data:
            p.stock_quantity = int(request.data.get("stock_quantity"))
        if "is_active" in request.data:
            p.is_active = bool(request.data.get("is_active"))
        p.embedding_status = "pending"
        p.save()
        return Response({"id": p.id, "name": p.name})
    p.is_active = False
    p.save(update_fields=["is_active"])
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_product_submit_approval(request, product_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    p = Product.objects.filter(id=product_id, business=business, vendor=vendor).first()
    if not p:
        return Response({"detail": "product not found"}, status=404)
    p.approval_status = "pending"
    p.save(update_fields=["approval_status"])
    return Response({"id": p.id, "approval_status": p.approval_status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_products_reindex(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    qs = Product.objects.filter(business=business, vendor=vendor)
    qs.update(embedding_status="pending")
    return Response({"status": "queued", "count": qs.count()})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_orders(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    qs = Order.objects.filter(business=business, vendor=vendor).order_by("-created_at")
    return Response(OrderSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_order_detail(request, order_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    o = Order.objects.filter(id=order_id, business=business, vendor=vendor).first()
    if not o:
        return Response({"detail": "order not found"}, status=404)
    return Response(OrderSerializer(o).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def vendor_order_status(request, order_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    o = Order.objects.filter(id=order_id, business=business, vendor=vendor).first()
    if not o:
        return Response({"detail": "order not found"}, status=404)
    val = str(request.data.get("status", "")).strip()
    allowed = {"confirmed", "processing", "shipped", "delivered"}
    if val not in allowed:
        return Response({"detail": "invalid vendor status"}, status=400)
    o.status = val
    o.save(update_fields=["status", "updated_at"])
    return Response({"id": o.id, "status": o.status})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_tickets(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    qs = Ticket.objects.filter(business=business, vendor=vendor).order_by("-created_at")
    return Response([{"id": t.id, "subject": t.subject, "status": t.status, "priority": t.priority, "order_id": t.order_id} for t in qs])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_ticket_detail(request, ticket_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    t = Ticket.objects.filter(id=ticket_id, business=business, vendor=vendor).first()
    if not t:
        return Response({"detail": "ticket not found"}, status=404)
    return Response({"id": t.id, "subject": t.subject, "details": t.details, "status": t.status, "priority": t.priority})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_ticket_comment(request, ticket_id):
    from apps.tickets.models import TicketComment

    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    t = Ticket.objects.filter(id=ticket_id, business=business, vendor=vendor).first()
    if not t:
        return Response({"detail": "ticket not found"}, status=404)
    text = str(request.data.get("text", "")).strip()
    if not text:
        return Response({"detail": "text is required"}, status=400)
    c = TicketComment.objects.create(ticket=t, author=request.user, text=text)
    return Response({"id": c.id, "text": c.text, "created_at": c.created_at}, status=201)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def vendor_ticket_status(request, ticket_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    t = Ticket.objects.filter(id=ticket_id, business=business, vendor=vendor).first()
    if not t:
        return Response({"detail": "ticket not found"}, status=404)
    val = str(request.data.get("status", "")).strip()
    if val not in dict(Ticket.STATUS_CHOICES):
        return Response({"detail": "invalid status"}, status=400)
    t.status = val
    t.save(update_fields=["status"])
    return Response({"id": t.id, "status": t.status})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def vendor_faqs(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    if request.method == "GET":
        qs = FAQ.objects.filter(business=business, vendor=vendor).order_by("-created_at")
        return Response([{"id": f.id, "question": f.question, "answer": f.answer, "category": f.category, "language": f.language} for f in qs])
    f = FAQ.objects.create(
        business=business,
        vendor=vendor,
        question=str(request.data.get("question", "")).strip(),
        answer=str(request.data.get("answer", "")).strip(),
        category=str(request.data.get("category", "")).strip(),
        tags=request.data.get("tags") or [],
        language=str(request.data.get("language", "bn")).strip() or "bn",
        embedding_status="pending",
    )
    return Response({"id": f.id}, status=201)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def vendor_faq_detail(request, faq_id):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    f = FAQ.objects.filter(id=faq_id, business=business, vendor=vendor).first()
    if not f:
        return Response({"detail": "faq not found"}, status=404)
    if request.method == "PATCH":
        for fld in ["question", "answer", "category", "language"]:
            if fld in request.data:
                setattr(f, fld, request.data.get(fld))
        if "tags" in request.data:
            f.tags = request.data.get("tags") or []
        f.embedding_status = "pending"
        f.save()
        return Response({"id": f.id})
    f.delete()
    return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_faqs_reindex(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    qs = FAQ.objects.filter(business=business, vendor=vendor)
    qs.update(embedding_status="pending")
    return Response({"status": "queued", "count": qs.count()})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def vendor_payouts(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    qs = VendorPayout.objects.filter(business=business, vendor=vendor).order_by("-requested_at")
    return Response(VendorPayoutSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def vendor_payout_request(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    settings_obj = _get_marketplace_settings(business)
    amount = Decimal(str(request.data.get("amount", "0")))
    if amount < settings_obj.min_payout_amount:
        return Response({"detail": f"minimum payout amount is {settings_obj.min_payout_amount}"}, status=400)
    payout = VendorPayout.objects.create(
        business=business,
        vendor=vendor,
        amount=amount,
        payout_method=str(request.data.get("payout_method", vendor.payout_method or settings_obj.default_payout_method or "bank")),
        status="pending",
    )
    return Response(VendorPayoutSerializer(payout).data, status=201)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def vendor_settings(request):
    business = get_user_business(request.user)
    vendor = get_vendor_for_user(request.user, business)
    if not vendor:
        return Response({"detail": "vendor not found"}, status=404)
    if request.method == "GET":
        return Response(VendorSerializer(vendor).data)
    serializer = VendorSerializer(vendor, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def storefront_create_order(request):
    business_id = request.data.get("business_id")
    vendor_id = request.data.get("vendor_id")
    business = None
    if business_id:
        from apps.businesses.models import Business

        business = Business.objects.filter(id=business_id).first()
    if not business and vendor_id:
        vendor = Vendor.objects.filter(id=vendor_id).first()
        business = vendor.business if vendor else None
    if not business:
        return Response({"detail": "business/vendor is required"}, status=400)

    vendor = Vendor.objects.filter(id=vendor_id, business=business, status="approved", is_active=True).first()
    if not vendor:
        return Response({"detail": "vendor not found/approved"}, status=404)

    customer_payload = request.data.get("customer") or {}
    phone = str(customer_payload.get("phone", "")).strip()
    email = str(customer_payload.get("email", "")).strip()
    external_id = phone or email or f"guest-{uuid.uuid4().hex[:8]}"
    customer, _ = CustomerProfile.objects.get_or_create(
        business=business,
        external_source="storefront",
        external_id=external_id,
        defaults={"name": str(customer_payload.get("name", "")).strip(), "metadata": {"email": email, "phone": phone}},
    )

    items = request.data.get("items") or []
    if not items:
        return Response({"detail": "items required"}, status=400)

    subtotal = Decimal("0")
    parsed_items = []
    for it in items:
        p = Product.objects.filter(id=it.get("product_id"), business=business, vendor=vendor, is_active=True, approval_status="approved").first()
        if not p:
            return Response({"detail": f"product not found/approved: {it.get('product_id')}"}, status=400)
        qty = max(1, int(it.get("quantity", 1)))
        if p.stock_quantity < qty:
            return Response({"detail": f"insufficient stock for {p.name}"}, status=400)
        price = p.sale_price if p.sale_price and p.sale_price > 0 else p.price
        total_price = Decimal(price) * qty
        subtotal += total_price
        parsed_items.append((p, qty, Decimal(price), total_price))

    delivery_fee = Decimal(str(request.data.get("delivery_fee", "80")))
    discount = Decimal(str(request.data.get("discount", "0")))
    total = subtotal + delivery_fee - discount
    order_number = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    order = Order.objects.create(
        business=business,
        vendor=vendor,
        customer=customer,
        order_number=order_number,
        status="pending",
        payment_status="unpaid",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        discount=discount,
        total=total,
        currency="BDT",
        delivery_address=str(request.data.get("delivery_address", "")),
        customer_phone=phone,
        customer_email=email,
        notes=str(request.data.get("notes", "")),
    )

    for p, qty, price, total_price in parsed_items:
        OrderItem.objects.create(
            order=order,
            product=p,
            vendor=vendor,
            product_name_snapshot=p.name,
            unit_price=price,
            quantity=qty,
            total_price=total_price,
        )
        p.stock_quantity = max(0, p.stock_quantity - qty)
        p.save(update_fields=["stock_quantity"])

    commission_rate = Decimal(vendor.commission_rate or 0)
    commission_amount = (total * commission_rate) / Decimal("100")
    vendor_earning = total - commission_amount
    VendorCommission.objects.create(
        business=business,
        vendor=vendor,
        order=order,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        vendor_earning=vendor_earning,
        status="pending",
    )

    if request.data.get("initial_support_note"):
        conv, _ = Conversation.objects.get_or_create(
            business=business,
            visitor_id=f"store:{customer.external_id}",
            defaults={"vendor": vendor, "order": order},
        )
        Message.objects.create(conversation=conv, role="customer", text=str(request.data.get("initial_support_note")))

    return Response({"order_number": order.order_number, "order_id": order.id, "total": str(order.total)}, status=201)


@api_view(["GET"])
@permission_classes([AllowAny])
def storefront_order_detail(request, order_number):
    order = Order.objects.filter(order_number=order_number).select_related("vendor", "customer").first()
    if not order:
        return Response({"detail": "order not found"}, status=404)
    return Response(OrderSerializer(order).data)
