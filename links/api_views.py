from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.api_views import _check_auth
from .models import Link
import json


@csrf_exempt
@require_POST
def link_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    if not name or not url:
        return JsonResponse({'success': False, 'error': 'name and url required'}, status=400)
    link = Link.objects.create(
        name=name,
        url=url,
        description=data.get('description', '').strip(),
        icon=data.get('icon', '🔗').strip() or '🔗',
        category=data.get('category', 'external').strip() or 'external',
        sort_order=Link.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': link.id, 'name': link.name, 'url': link.url})


@csrf_exempt
@require_POST
def link_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        link = Link.objects.get(pk=pk)
    except Link.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    if data.get('name', '').strip():
        link.name = data['name'].strip()
    if data.get('url', '').strip():
        link.url = data['url'].strip()
    if 'description' in data:
        link.description = data['description'].strip()
    if data.get('icon', '').strip():
        link.icon = data['icon'].strip()
    if data.get('category', '').strip():
        link.category = data['category'].strip()
    link.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def link_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Link.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Link.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


@csrf_exempt
def link_list(request):
    links = Link.objects.filter(is_visible=True).values('id', 'name', 'url', 'description', 'icon', 'category')
    return JsonResponse({'success': True, 'links': list(links)})
