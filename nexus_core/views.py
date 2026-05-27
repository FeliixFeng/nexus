from django.shortcuts import render
from blog.models import Post
from links.models import Link


def home(request):
    """首页"""
    # 最新文章（最多显示6篇）
    recent_posts = Post.objects.filter(status='published')[:6]
    
    # 链接按分类分组
    all_links = Link.objects.filter(is_visible=True)
    services = all_links.filter(category='service')
    external = all_links.filter(category='external')
    projects = all_links.filter(category='project')
    
    context = {
        'recent_posts': recent_posts,
        'services': services,
        'external': external,
        'projects': projects,
        'all_links': all_links,
    }
    return render(request, 'core/home.html', context)
