from django.shortcuts import render
from django.conf import settings
from blog.models import Post
from links.models import Link
from nexus_core.models import Activity, NowItem
from nexus_core.pin_utils import is_pin_verified


def home(request):
    """首页"""
    from django.db.models import Q
    
    # 获取最新一条科技日报
    latest_daily = Post.objects.filter(
        status='published',
        tags__name='科技日报'
    ).order_by('-created_at').first()
    
    # 获取其他笔记（排除科技日报）
    other_posts = Post.objects.filter(
        status='published'
    ).exclude(tags__name='科技日报').order_by('-created_at')[:5]
    
    # 合并：日报在最前面
    recent_posts = []
    if latest_daily:
        recent_posts.append(latest_daily)
    recent_posts.extend(other_posts)
    
    all_links = Link.objects.filter(is_visible=True)
    activities = Activity.objects.filter(is_visible=True).order_by('sort_order')[:6]
    now_items = NowItem.objects.all()[:5]

    context = {
        'recent_posts': recent_posts,
        'services': all_links.filter(category='service'),
        'external': all_links.filter(category='external'),
        'projects': all_links.filter(category='project'),
        'all_links': all_links,
        'activities': activities,
        'now_items': now_items,
        'is_editor': is_pin_verified(request),
    }
    return render(request, 'core/home.html', context)


def now_page(request):
    """动态页 — 纯展示，完成按钮需要 API Key"""
    return render(request, 'core/now.html', {
        'now_items': NowItem.objects.all(),
        'activities': Activity.objects.filter(is_visible=True).order_by('sort_order'),
        'NEXUS_API_KEY': settings.NEXUS_API_KEY,
    })
