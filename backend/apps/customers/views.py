from django.http import JsonResponse


def health(request):
    return JsonResponse({'app': 'customers', 'status': 'ok'})
