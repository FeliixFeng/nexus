from django.shortcuts import render, redirect
from django.urls import reverse
from links.models import Link
from nexus_core.models import Activity, NowItem
from nexus_core.pin_utils import is_pin_verified


def home(request):
    """首页 — 身份、常用链接、状态摘要"""
    all_links = Link.objects.filter(is_visible=True)
    activities = Activity.objects.filter(is_visible=True).order_by('sort_order', '-created_at')[:4]
    now_items = NowItem.objects.all()[:5]

    return render(request, 'nexus_core/home.html', {
        'all_links': all_links[:8],
        'services': all_links.filter(category='service'),
        'projects': all_links.filter(category='project'),
        'activities': activities,
        'now_items': now_items,
        'is_editor': is_pin_verified(request),
    })


def status_page(request):
    """状态 — 进行中 + 里程碑"""
    return render(request, 'nexus_core/status.html', {
        'now_items': NowItem.objects.all(),
        'activities': Activity.objects.filter(is_visible=True).order_by('sort_order', '-created_at'),
        'is_editor': is_pin_verified(request),
    })


def now_page(request):
    """兼容旧地址"""
    return redirect('nexus_core:status_page')


def other_page(request):
    """其他 — 关于 / 说明 / 个性化 / 扩展位"""
    return render(request, 'nexus_core/other.html', {
        'is_editor': is_pin_verified(request),
    })
