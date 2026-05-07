from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile
from apps.billing.models import PricingPlan, Subscription
from apps.businesses.models import Business
from apps.conversations.models import Conversation, Message
from apps.customers.models import CustomerProfile
from apps.faqs.models import FAQ
from apps.marketplace.models import Order, OrderItem, Vendor, VendorCommission, VendorPayout, VendorStaff
from apps.products.models import Product
from apps.tenants.models import TeamMember
from apps.tickets.models import Ticket


class Command(BaseCommand):
    help = 'Seed SupportBond multi-vendor demo data'

    def handle(self, *args, **options):
        def mk_user(username, full_name, phone, role):
            user, _ = User.objects.get_or_create(username=username, defaults={'email': username})
            user.set_password('password123')
            user.save()
            UserProfile.objects.update_or_create(user=user, defaults={'full_name': full_name, 'phone': phone, 'role': role})
            return user

        marketplace_user = mk_user('marketplace@supportbond.ai', 'Marketplace Owner', '01799999999', 'owner')
        vendor1_user = mk_user('vendor1@supportbond.ai', 'Vendor One', '01733333333', 'manager')
        vendor2_user = mk_user('vendor2@supportbond.ai', 'Vendor Two', '01744444444', 'manager')
        agent = mk_user('agent@supportbond.ai', 'Support Agent', '01800000000', 'agent')

        plans = [
            ('starter', 'Starter', 999, 1000, 3, 100, 1000, 3, 1000, ['website', 'messenger']),
            ('pro', 'Pro', 6999, 20000, 20, 2000, 100000, 20, 15000, ['website', 'messenger', 'whatsapp']),
            ('business', 'Business', 14999, 100000, 999999, 999999, 999999, 999999, 999999, ['website', 'messenger', 'whatsapp', 'api']),
        ]
        for code, name, price, msg_limit, vendor_limit, p_limit, order_limit, agent_limit, ai_reply_limit, channels in plans:
            PricingPlan.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'monthly_price': price,
                    'message_limit': msg_limit,
                    'seat_limit': max(1, agent_limit),
                    'vendor_limit': vendor_limit,
                    'product_limit_per_vendor': p_limit,
                    'order_limit': order_limit,
                    'agent_limit': agent_limit,
                    'ai_reply_limit': ai_reply_limit,
                    'channels_allowed': channels,
                    'features': {'vendor_limit': vendor_limit, 'product_limit_per_vendor': p_limit},
                    'is_active': True,
                },
            )

        business, _ = Business.objects.update_or_create(
            slug='shobar-shonge-demo-marketplace',
            defaults={
                'owner': marketplace_user,
                'name': 'Shobar Shonge Demo Marketplace',
                'website': 'https://market.example.com',
                'welcome_message': 'Welcome to SupportBond marketplace support',
                'handover_enabled': True,
            },
        )
        Subscription.objects.update_or_create(business=business, defaults={'plan': PricingPlan.objects.get(code='pro'), 'status': 'active'})
        TeamMember.objects.update_or_create(business=business, user=marketplace_user, defaults={'role': 'owner', 'is_active': True})
        TeamMember.objects.update_or_create(business=business, user=agent, defaults={'role': 'agent', 'is_active': True})

        vendor_specs = [
            ('Trendy BD Fashion', 'trendy-bd-fashion', vendor1_user),
            ('Dhaka Gadget Zone', 'dhaka-gadget-zone', vendor2_user),
            ('Smart Coaching Center', 'smart-coaching-center', marketplace_user),
            ('Healthy Life Clinic', 'healthy-life-clinic', marketplace_user),
        ]

        customer_names = ['Rahim Ahmed', 'Fatima Khan', 'Karim Hossain', 'Nusrat Jahan', 'Tanvir Islam']

        for idx, (vname, vslug, vowner) in enumerate(vendor_specs, start=1):
            vendor, _ = Vendor.objects.update_or_create(
                business=business,
                slug=vslug,
                defaults={
                    'owner_user': vowner,
                    'name': vname,
                    'status': 'approved',
                    'is_active': True,
                    'commission_rate': Decimal('10.00'),
                    'city': 'Dhaka',
                    'return_policy': '? ????? ????? ???????',
                    'delivery_policy': '????? ????? ?-? ???, ????? ?-? ???',
                    'support_email': f'{vslug}@supportbond.ai',
                    'support_phone': f'+88017000000{idx}',
                },
            )
            VendorStaff.objects.update_or_create(vendor=vendor, user=vowner, defaults={'role': 'vendor_owner', 'is_active': True})

            for i in range(1, 11):
                product, _ = Product.objects.update_or_create(
                    business=business,
                    vendor=vendor,
                    slug=f'{vslug}-product-{i}',
                    defaults={
                        'name': f'{vname} Product {i}',
                        'description': 'Demo marketplace product',
                        'price': Decimal('500.00') + i * 50,
                        'sale_price': Decimal('0'),
                        'currency': 'BDT',
                        'stock_quantity': 100,
                        'stock_status': 'in_stock',
                        'approval_status': 'approved',
                        'is_active': True,
                        'embedding_status': 'pending',
                    },
                )
                FAQ.objects.update_or_create(
                    business=business,
                    vendor=vendor,
                    question=f'{vname} FAQ {i}',
                    defaults={'answer': '???????? ?-? ????? ??????', 'category': 'delivery', 'language': 'bn', 'is_active': True, 'embedding_status': 'pending'},
                )

                cname = customer_names[(i - 1) % len(customer_names)]
                customer, _ = CustomerProfile.objects.get_or_create(
                    business=business,
                    vendor=vendor,
                    external_source='website',
                    external_id=f'{vslug}-cust-{i}',
                    defaults={'name': cname, 'metadata': {'phone': f'+88017123{i:04d}'}},
                )
                order, _ = Order.objects.get_or_create(
                    business=business,
                    vendor=vendor,
                    customer=customer,
                    order_number=f'ORD-{vslug[:4].upper()}-{i:03d}',
                    defaults={
                        'status': 'pending',
                        'payment_status': 'unpaid',
                        'subtotal': product.price,
                        'delivery_fee': Decimal('80.00'),
                        'discount': Decimal('0.00'),
                        'total': product.price + Decimal('80.00'),
                        'currency': 'BDT',
                        'delivery_address': 'Dhanmondi, Dhaka',
                        'customer_phone': customer.metadata.get('phone', ''),
                    },
                )
                OrderItem.objects.get_or_create(
                    order=order,
                    product=product,
                    vendor=vendor,
                    defaults={'product_name_snapshot': product.name, 'unit_price': product.price, 'quantity': 1, 'total_price': product.price},
                )
                commission, _ = VendorCommission.objects.get_or_create(
                    business=business,
                    vendor=vendor,
                    order=order,
                    defaults={
                        'commission_rate': vendor.commission_rate,
                        'commission_amount': order.total * vendor.commission_rate / Decimal('100'),
                        'vendor_earning': order.total - (order.total * vendor.commission_rate / Decimal('100')),
                        'status': 'confirmed',
                    },
                )
                VendorPayout.objects.get_or_create(
                    business=business,
                    vendor=vendor,
                    amount=commission.vendor_earning,
                    defaults={'status': 'pending', 'payout_method': 'bank'},
                )

                conv, _ = Conversation.objects.get_or_create(
                    business=business,
                    visitor_id=f'market:{customer.external_id}',
                    defaults={'vendor': vendor, 'order': order, 'product': product},
                )
                Message.objects.get_or_create(conversation=conv, role='customer', text='???? ?????? ??????')
                Message.objects.get_or_create(conversation=conv, role='ai', text='????? ?????? ???????? ? ????')
                Ticket.objects.get_or_create(
                    business=business,
                    conversation=conv,
                    vendor=vendor,
                    order=order,
                    product=product,
                    subject='Vendor order support',
                    defaults={'details': 'Customer asked order status', 'status': 'open', 'priority': 'high', 'assignment_type': 'vendor'},
                )

        self.stdout.write(self.style.SUCCESS('Seed complete: marketplace@supportbond.ai, vendor1@supportbond.ai, vendor2@supportbond.ai, agent@supportbond.ai / password123'))
