from __future__ import annotations

import re

from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Business


def _extract_logo_data(uploaded_file) -> dict:
    data = {
        'file_name': uploaded_file.name,
        'content_type': getattr(uploaded_file, 'content_type', '') or '',
        'size_bytes': int(getattr(uploaded_file, 'size', 0) or 0),
        'detected_text': '',
        'suggested_business_name': '',
        'suggested_category': '',
    }

    base_name = uploaded_file.name.rsplit('.', 1)[0]
    cleaned = re.sub(r'[_\-]+', ' ', base_name).strip()
    if cleaned:
        data['suggested_business_name'] = cleaned.title()

    lower_name = cleaned.lower()
    if any(k in lower_name for k in ['clinic', 'dental', 'hospital', 'doctor']):
        data['suggested_category'] = 'clinic'
    elif any(k in lower_name for k in ['coach', 'academy', 'class', 'tuition']):
        data['suggested_category'] = 'coaching'
    elif any(k in lower_name for k in ['service', 'repair', 'maintenance']):
        data['suggested_category'] = 'service'
    else:
        data['suggested_category'] = 'shop'

    try:
        from PIL import Image  # type: ignore

        img = Image.open(uploaded_file)
        data['image_width'] = img.width
        data['image_height'] = img.height
        uploaded_file.seek(0)
    except Exception:
        uploaded_file.seek(0)

    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        img = Image.open(uploaded_file)
        extracted = (pytesseract.image_to_string(img) or '').strip()
        uploaded_file.seek(0)
        if extracted:
            data['detected_text'] = extracted[:500]
            if not data['suggested_business_name']:
                first_line = extracted.splitlines()[0].strip()
                if first_line:
                    data['suggested_business_name'] = first_line[:80]
    except Exception:
        uploaded_file.seek(0)

    return data


@api_view(['GET', 'POST', 'PATCH'])
def business_setup(request):
    business = Business.objects.filter(owner=request.user).first()

    if request.method == 'GET':
        if not business:
            return Response({'detail': 'business not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize(business))

    payload = {
        'name': request.data.get('name', ''),
        'slug': request.data.get('slug', ''),
        'website': request.data.get('website', ''),
        'welcome_message': request.data.get('welcome_message', 'Hello! How can I help you today?'),
        'handover_enabled': request.data.get('handover_enabled', True),
        'category': request.data.get('category', 'shop'),
        'support_email': request.data.get('support_email', ''),
        'support_phone': request.data.get('support_phone', ''),
        'business_hours': request.data.get('business_hours', ''),
        'address': request.data.get('address', ''),
    }

    if not payload['slug'] and payload['name']:
        payload['slug'] = slugify(payload['name'])

    if not business:
        if not payload['name'] or not payload['slug']:
            return Response({'detail': 'name and slug are required'}, status=status.HTTP_400_BAD_REQUEST)
        business = Business.objects.create(owner=request.user, **payload)
        return Response(_serialize(business), status=201)

    for key, value in payload.items():
        if key in request.data:
            setattr(business, key, value)
    business.save()
    return Response(_serialize(business))


@api_view(['POST'])
def upload_logo(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    logo = request.FILES.get('logo')
    if not logo:
        return Response({'detail': 'logo file is required'}, status=status.HTTP_400_BAD_REQUEST)

    max_bytes = 2 * 1024 * 1024
    if logo.size > max_bytes:
        return Response({'detail': 'logo size must be <= 2MB'}, status=status.HTTP_400_BAD_REQUEST)

    extracted_data = _extract_logo_data(logo)
    business.logo = logo
    business.logo_extracted_data = extracted_data
    business.save(update_fields=['logo', 'logo_extracted_data', 'updated_at'])

    return Response(
        {
            'logo_url': request.build_absolute_uri(business.logo.url) if business.logo else '',
            'extracted_data': extracted_data,
        }
    )


def _serialize(business: Business):
    return {
        'id': business.id,
        'name': business.name,
        'slug': business.slug,
        'website': business.website,
        'welcome_message': business.welcome_message,
        'handover_enabled': business.handover_enabled,
        'category': business.category,
        'support_email': business.support_email,
        'support_phone': business.support_phone,
        'business_hours': business.business_hours,
        'address': business.address,
        'logo_url': business.logo.url if business.logo else '',
        'logo_extracted_data': business.logo_extracted_data or {},
    }
