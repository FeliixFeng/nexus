from django.shortcuts import render
from blog.models import Post
from links.models import Link
from nexus_core.models import Activity, NowItem
from nexus_core.pin_utils import is_pin_verified


def home(request):
    """首页"""
    recent_posts = Post.objects.filter(status='published')[:6]
    all_links = Link.objects.filter(is_visible=True)
    activities = Activity.objects.filter(is_visible=True)[:6]

    context = {
        'recent_posts': recent_posts,
        'services': all_links.filter(category='service'),
        'external': all_links.filter(category='external'),
        'projects': all_links.filter(category='project'),
        'all_links': all_links,
        'activities': activities,
        'is_editor': is_pin_verified(request),
    }
    return render(request, 'core/home.html', context)


def now_page(request):
    """动态页 — 纯展示"""
    return render(request, 'core/now.html', {
        'now_items': NowItem.objects.all(),
        'activities': Activity.objects.filter(is_visible=True),
    })
