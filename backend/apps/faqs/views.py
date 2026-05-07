from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_gateway.services import build_embedding
from apps.businesses.access import get_user_business
from .models import FAQ


def _safe_embedding(text: str):
    try:
        return build_embedding(text)
    except Exception:
        return None


@api_view(['GET', 'POST'])
def faq_list_create(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        data = [_serialize(faq) for faq in FAQ.objects.filter(business=business).order_by('-created_at')]
        return Response(data)

    question = request.data.get('question', '').strip()
    answer = request.data.get('answer', '').strip()
    if not question or not answer:
        return Response({'detail': 'question and answer are required'}, status=status.HTTP_400_BAD_REQUEST)

    embedding = _safe_embedding(f"{question} {answer}")
    faq = FAQ.objects.create(
        business=business,
        question=question,
        answer=answer,
        category=str(request.data.get('category', '')).strip(),
        tags=request.data.get('tags', []) or [],
        language=str(request.data.get('language', 'bn')).strip() or 'bn',
        embedding_status='pending' if embedding is not None else 'failed',
        embedding_vector=embedding,
    )
    return Response(_serialize(faq), status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
def faq_detail(request, faq_id):
    business = get_user_business(request.user)
    faq = FAQ.objects.filter(id=faq_id, business=business).first()
    if not faq:
        return Response({'detail': 'faq not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(_serialize(faq))

    if request.method == 'PATCH':
        if 'question' in request.data:
            faq.question = request.data['question']
        if 'answer' in request.data:
            faq.answer = request.data['answer']
        if 'category' in request.data:
            faq.category = str(request.data.get('category', ''))
        if 'tags' in request.data:
            faq.tags = request.data.get('tags') or []
        if 'language' in request.data:
            faq.language = str(request.data.get('language', 'bn')) or 'bn'
        if 'is_active' in request.data:
            faq.is_active = bool(request.data['is_active'])
        if 'question' in request.data or 'answer' in request.data:
            emb = _safe_embedding(f"{faq.question} {faq.answer}")
            faq.embedding_vector = emb
            faq.embedding_status = 'pending' if emb is not None else 'failed'
        faq.save()
        return Response(_serialize(faq))

    faq.delete()
    return Response(status=204)


def _serialize(faq: FAQ):
    return {
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'category': faq.category,
        'tags': faq.tags,
        'language': faq.language,
        'embedding_status': faq.embedding_status,
        'is_active': faq.is_active,
        'has_embedding': bool(faq.embedding_vector),
        'created_at': faq.created_at,
    }


@api_view(['POST'])
def faq_bulk_import(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    items = request.data.get('items') or []
    created = 0
    for item in items:
        q = str(item.get('question', '')).strip()
        a = str(item.get('answer', '')).strip()
        if not q or not a:
            continue
        emb = _safe_embedding(f"{q} {a}")
        FAQ.objects.create(
            business=business,
            question=q,
            answer=a,
            category=str(item.get('category', '')).strip(),
            tags=item.get('tags') or [],
            language=str(item.get('language', 'bn')).strip() or 'bn',
            embedding_status='pending' if emb is not None else 'failed',
            embedding_vector=emb,
        )
        created += 1
    return Response({'created': created}, status=201)


@api_view(['POST'])
def faq_reindex(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    faqs = FAQ.objects.filter(business=business)
    for faq in faqs:
        faq.embedding_status = 'pending'
        faq.save(update_fields=['embedding_status'])
    return Response({'status': 'queued', 'count': faqs.count()})
