from django.http import JsonResponse


def health(request):
    return JsonResponse({'app': 'ai_gateway', 'status': 'ok'})
