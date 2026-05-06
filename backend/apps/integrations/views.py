from django.http import JsonResponse


def health(request):
    return JsonResponse({'app': 'integrations', 'status': 'ok'})
