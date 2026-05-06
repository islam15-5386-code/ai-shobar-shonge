from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.models import Business
from .models import FAQ


@api_view(['GET', 'POST'])
def faq_list_create(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        data = [_serialize(faq) for faq in FAQ.objects.filter(business=business).order_by('-created_at')]
        return Response(data)

    question = request.data.get('question', '').strip()
    answer = request.data.get('answer', '').strip()
    if not question or not answer:
        return Response({'detail': 'question and answer are required'}, status=status.HTTP_400_BAD_REQUEST)

    faq = FAQ.objects.create(business=business, question=question, answer=answer)
    return Response(_serialize(faq), status=201)


@api_view(['GET', 'PATCH', 'DELETE'])
def faq_detail(request, faq_id):
    business = Business.objects.filter(owner=request.user).first()
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
        if 'is_active' in request.data:
            faq.is_active = bool(request.data['is_active'])
        faq.save()
        return Response(_serialize(faq))

    faq.delete()
    return Response(status=204)


def _serialize(faq: FAQ):
    return {
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'is_active': faq.is_active,
        'created_at': faq.created_at,
    }
