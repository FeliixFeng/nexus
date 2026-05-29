from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.pin_utils import is_pin_verified
from .models import Activity
import json


def _check_auth(request):
    """检查 PIN 验证"""
    return is_pin_verified(request)


@require_POST
def activity_create(request):
    """创建动态"""
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)

    text = request.POST.get('text', '').strip()
    date_label = request.POST.get('date_label', '').strip()
    if not text or not date_label:
        return JsonResponse({'success': False, 'error': '内容不能为空'}, status=400)

    act = Activity.objects.create(
        text=text,
        date_label=date_label,
        sort_order=Activity.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': act.id, 'text': act.text, 'date_label': act.date_label})


@require_POST
def activity_update(request, pk):
    """更新动态"""
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)

    try:
        act = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)

    text = request.POST.get('text', '').strip()
    date_label = request.POST.get('date_label', '').strip()
    if not text or not date_label:
        return JsonResponse({'success': False, 'error': '内容不能为空'}, status=400)

    act.text = text
    act.date_label = date_label
    act.save()
    return JsonResponse({'success': True})


@require_POST
def activity_delete(request, pk):
    """删除动态"""
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)

    try:
        act = Activity.objects.get(pk=pk)
        act.delete()
        return JsonResponse({'success': True})
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
