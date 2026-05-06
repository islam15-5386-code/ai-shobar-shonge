from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.accounts.models import UserProfile
from apps.ai_gateway.models import AIInteractionLog
from apps.billing.models import PricingPlan, Subscription
from apps.businesses.models import Business
from apps.conversations.models import Conversation, Message
from apps.customers.models import CustomerProfile
from apps.faqs.models import FAQ
from apps.products.models import Product
from apps.tenants.models import TeamMember
from apps.tickets.models import Ticket


class Command(BaseCommand):
    help = 'Seed full SupportBond AI demo dataset'

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(username='owner@supportbond.ai', defaults={'email': 'owner@supportbond.ai'})
        owner.set_password('password123')
        owner.save()
        UserProfile.objects.update_or_create(user=owner, defaults={'full_name': 'Owner User', 'phone': '01700000000', 'role': 'owner'})

        agent, _ = User.objects.get_or_create(username='agent@supportbond.ai', defaults={'email': 'agent@supportbond.ai'})
        agent.set_password('password123')
        agent.save()
        UserProfile.objects.update_or_create(user=agent, defaults={'full_name': 'Agent User', 'phone': '01800000000', 'role': 'agent'})

        manager, _ = User.objects.get_or_create(username='manager@supportbond.ai', defaults={'email': 'manager@supportbond.ai'})
        manager.set_password('password123')
        manager.save()
        UserProfile.objects.update_or_create(user=manager, defaults={'full_name': 'Manager User', 'phone': '01900000000', 'role': 'manager'})

        plans = [
            ('starter', 'Starter', 999, 1000, 1, {'website_chatbot': True}),
            ('growth', 'Growth', 2999, 5000, 3, {'website_chatbot': True, 'messenger': True}),
            ('pro', 'Pro', 6999, 20000, 10, {'website_chatbot': True, 'messenger': True, 'whatsapp': True, 'voice_to_text': True}),
        ]
        for code, name, price, limit, seats, features in plans:
            PricingPlan.objects.update_or_create(
                code=code,
                defaults={'name': name, 'monthly_price': price, 'message_limit': limit, 'seat_limit': seats, 'features': features, 'is_active': True},
            )

        owner2, _ = User.objects.get_or_create(username='owner2@supportbond.ai', defaults={'email': 'owner2@supportbond.ai'})
        owner2.set_password('password123')
        owner2.save()
        UserProfile.objects.update_or_create(user=owner2, defaults={'full_name': 'Owner Two', 'phone': '01711111111', 'role': 'owner'})

        owner3, _ = User.objects.get_or_create(username='owner3@supportbond.ai', defaults={'email': 'owner3@supportbond.ai'})
        owner3.set_password('password123')
        owner3.save()
        UserProfile.objects.update_or_create(user=owner3, defaults={'full_name': 'Owner Three', 'phone': '01722222222', 'role': 'owner'})

        businesses = [
            ('Demo Fashion Shop', 'demo-fashion-shop', 'https://fashion.example.com', owner),
            ('Demo Coaching Center', 'demo-coaching-center', 'https://coaching.example.com', owner2),
            ('Demo Dental Clinic', 'demo-dental-clinic', 'https://dental.example.com', owner3),
        ]

        for idx, (name, slug, site, owner_user) in enumerate(businesses, start=1):
            business, _ = Business.objects.update_or_create(
                slug=slug,
                defaults={'owner': owner_user, 'name': name, 'website': site, 'welcome_message': 'স্বাগতম! কিভাবে সাহায্য করতে পারি?', 'handover_enabled': True},
            )
            plan = PricingPlan.objects.get(code='pro' if idx == 3 else 'growth')
            Subscription.objects.update_or_create(business=business, defaults={'plan': plan, 'status': 'active'})
            TeamMember.objects.update_or_create(business=business, user=owner_user, defaults={'role': 'owner', 'is_active': True})
            TeamMember.objects.update_or_create(business=business, user=manager, defaults={'role': 'manager', 'is_active': True})
            TeamMember.objects.update_or_create(business=business, user=agent, defaults={'role': 'agent', 'is_active': True})

            for i in range(1, 21):
                FAQ.objects.update_or_create(
                    business=business,
                    question=f'{name} FAQ {i} - ডেলিভারি/সার্ভিস তথ্য?',
                    defaults={
                        'answer': f'{name} এর সাপোর্ট উত্তর {i}।',
                        'category': 'general',
                        'tags': ['bangla', 'support'],
                        'language': 'bn',
                        'embedding_status': 'pending',
                        'is_active': True,
                    },
                )

            for i in range(1, 11):
                Product.objects.update_or_create(
                    business=business,
                    name=f'{name} Product/Service {i}',
                    defaults={
                        'description': 'বাংলাদেশি গ্রাহকদের জন্য ডেমো পণ্য/সেবা',
                        'price': 500 + i * 100,
                        'currency': 'BDT',
                        'stock_status': 'in_stock',
                        'category': 'demo',
                        'delivery_info': 'ঢাকার ভিতরে ১-২ দিন',
                        'return_policy': '৭ দিনের মধ্যে রিটার্ন',
                        'warranty_info': 'ডেমো ওয়ারেন্টি',
                        'is_active': True,
                        'embedding_status': 'pending',
                    },
                )

            customer, _ = CustomerProfile.objects.get_or_create(
                business=business,
                external_source='website',
                external_id=f'{slug}-cust-1',
                defaults={'name': 'Rahim Uddin', 'metadata': {'location': 'Dhaka, Bangladesh'}},
            )
            conversation, _ = Conversation.objects.get_or_create(business=business, visitor_id=f'web:{customer.external_id}')
            Message.objects.get_or_create(conversation=conversation, role='customer', text='রিফান্ড কীভাবে পাবো?')
            Message.objects.get_or_create(conversation=conversation, role='ai', text='রিফান্ডের জন্য ৭ দিনের মধ্যে আবেদন করুন।')
            ticket, _ = Ticket.objects.get_or_create(
                business=business,
                conversation=conversation,
                subject='Customer refund request',
                defaults={'details': 'Needs follow-up', 'status': 'open', 'priority': 'high', 'assigned_agent': agent},
            )
            _ = ticket
            AIInteractionLog.objects.get_or_create(
                business=business,
                conversation=conversation,
                user_message='রিফান্ড কীভাবে পাবো?',
                defaults={'ai_reply': 'রিফান্ডের জন্য ৭ দিনের মধ্যে আবেদন করুন।', 'confidence': 0.72, 'intent': 'refund', 'sentiment': 'neutral'},
            )

        self.stdout.write(self.style.SUCCESS('Demo seed completed. owner@supportbond.ai / password123, agent@supportbond.ai / password123'))
