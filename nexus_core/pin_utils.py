import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def verify_pin(request):
    """验证PIN码"""
    try:
        data = json.loads(request.body)
        pin = data.get('pin', '')
        
        # 支持4位或6位PIN
        if pin == settings.NEXUS_PIN:
            request.session['pin_verified'] = True
            request.session.set_expiry(86400 * 7)  # 7天有效
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': '密码错误'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def is_pin_verified(request):
    """检查PIN是否已验证"""
    return request.session.get('pin_verified', False)


@csrf_exempt
@require_http_methods(["POST"])
def lock_pin(request):
    """锁定，清除PIN状态"""
    request.session.pop('pin_verified', None)
    return JsonResponse({'success': True})
