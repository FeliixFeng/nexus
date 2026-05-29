from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.pin_utils import is_pin_verified
from .models import Activity, NowItem
import json


def _check_auth(request):
    """检查 PIN 验证"""
    return is_pin_verified(request)


# ─── NowItem CRUD ───────────────────────────────────

@require_POST
def now_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    text = request.POST.get('text', '').strip()
    icon = request.POST.get('icon', '📌').strip() or '📌'
    if not text:
        return JsonResponse({'success': False, 'error': '内容不能为空'}, status=400)
    item = NowItem.objects.create(
        text=text, icon=icon,
        sort_order=NowItem.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': item.id})


@require_POST
def now_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        item = NowItem.objects.get(pk=pk)
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = request.POST.get('text', '').strip()
    icon = request.POST.get('icon', '').strip()
    if text:
        item.text = text
    if icon:
        item.icon = icon
    item.save()
    return JsonResponse({'success': True})


@require_POST
def now_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        NowItem.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


# ─── Activity CRUD ──────────────────────────────────

@require_POST
def activity_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    text = request.POST.get('text', '').strip()
    icon = request.POST.get('icon', '📌').strip() or '📌'
    date_label = request.POST.get('date_label', '').strip()
    if not text or not date_label:
        return JsonResponse({'success': False, 'error': '内容不能为空'}, status=400)
    act = Activity.objects.create(
        text=text, icon=icon, date_label=date_label,
        sort_order=Activity.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': act.id})


@require_POST
def activity_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        act = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = request.POST.get('text', '').strip()
    icon = request.POST.get('icon', '').strip()
    date_label = request.POST.get('date_label', '').strip()
    if text:
        act.text = text
    if icon:
        act.icon = icon
    if date_label:
        act.date_label = date_label
    act.save()
    return JsonResponse({'success': True})


@require_POST
def activity_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Activity.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
