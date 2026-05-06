from django.http import JsonResponse


def health(request):
    return JsonResponse({'app': 'faqs', 'status': 'ok'})
