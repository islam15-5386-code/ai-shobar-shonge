from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.billing.models import PricingPlan, Subscription
from apps.businesses.models import Business
from apps.faqs.models import FAQ


class Command(BaseCommand):
    help = 'Seed Bangladeshi demo data for AI support SaaS'

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            username='demo_owner',
            defaults={'email': 'demo@shobarshonge.ai'},
        )
        owner.set_password('demo12345')
        owner.save()

        plans = [
            ('starter', 'Starter', 999, 1000, 1, {'website_chatbot': True}),
            ('growth', 'Growth', 2999, 5000, 3, {'website_chatbot': True, 'messenger': True, 'ticket_management': True}),
            ('pro', 'Pro', 6999, 15000, 10, {'website_chatbot': True, 'messenger': True, 'whatsapp': True, 'voice_to_text': True, 'analytics': True}),
        ]
        for code, name, price, msg_limit, seat_limit, features in plans:
            PricingPlan.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'monthly_price': price,
                    'message_limit': msg_limit,
                    'seat_limit': seat_limit,
                    'features': features,
                    'is_active': True,
                },
            )

        business, _ = Business.objects.update_or_create(
            owner=owner,
            defaults={
                'name': 'Dhaka Fashion House',
                'slug': 'dhaka-fashion-house',
                'website': 'https://dhakafashion.example.com',
                'welcome_message': 'আসসালামু আলাইকুম! কিভাবে সাহায্য করতে পারি?',
                'handover_enabled': True,
            },
        )
        plan = PricingPlan.objects.get(code='growth')
        Subscription.objects.update_or_create(
            business=business,
            defaults={'plan': plan, 'status': 'active'},
        )
        FAQ.objects.update_or_create(
            business=business,
            question='ডেলিভারি কতদিন লাগে?',
            defaults={'answer': 'ঢাকার ভিতরে ১-২ দিন, ঢাকার বাইরে ৩-৫ দিন।', 'is_active': True},
        )
        FAQ.objects.update_or_create(
            business=business,
            question='রিফান্ড পলিসি কি?',
            defaults={'answer': 'ডেলিভারির ৭ দিনের মধ্যে রিফান্ড রিকোয়েস্ট করা যাবে।', 'is_active': True},
        )

        self.stdout.write(self.style.SUCCESS('Bangladeshi seed data created. username=demo_owner password=demo12345'))
