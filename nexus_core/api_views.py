from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.pin_utils import is_pin_verified
from .models import Activity, NowItem
from django.conf import settings
from datetime import date
import json


def _check_auth(request):
    api_key = request.headers.get('X-Nexus-Key', '')
    if api_key and api_key == settings.NEXUS_API_KEY:
        return True
    return is_pin_verified(request)


@csrf_exempt
@require_POST
def now_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    text = data.get('text', '').strip()
    icon = data.get('icon', '📌').strip() or '📌'
    if not text:
        return JsonResponse({'success': False, 'error': 'text required'}, status=400)
    item = NowItem.objects.create(
        text=text, icon=icon,
        sort_order=NowItem.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': item.id, 'icon': item.icon, 'text': item.text})


@csrf_exempt
@require_POST
def now_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        item = NowItem.objects.get(pk=pk)
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = data.get('text', '').strip()
    icon = data.get('icon', '').strip()
    if text:
        item.text = text
    if icon:
        item.icon = icon
    item.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def now_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        NowItem.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


@csrf_exempt
@require_POST
def now_complete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        item = NowItem.objects.get(pk=pk)
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    today = date.today()
    act = Activity.objects.create(
        text=item.text,
        icon=item.icon,
        date_label=f'{today.year}.{today.month:02d}.{today.day:02d}',
        sort_order=0,
    )
    item.delete()
    return JsonResponse({'success': True, 'id': act.id})


@csrf_exempt
@require_POST
def activity_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    text = data.get('text', '').strip()
    icon = data.get('icon', '📌').strip() or '📌'
    date_label = data.get('date_label', '').strip()
    if not text or not date_label:
        return JsonResponse({'success': False, 'error': 'text and date_label required'}, status=400)
    act = Activity.objects.create(
        text=text, icon=icon, date_label=date_label,
        sort_order=Activity.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': act.id, 'icon': act.icon, 'text': act.text, 'date_label': act.date_label})


@csrf_exempt
@require_POST
def activity_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        act = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = data.get('text', '').strip()
    icon = data.get('icon', '').strip()
    date_label = data.get('date_label', '').strip()
    if text:
        act.text = text
    if icon:
        act.icon = icon
    if date_label:
        act.date_label = date_label
    act.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def activity_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Activity.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
