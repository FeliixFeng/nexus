from django.shortcuts import render
from .models import Link


def link_list(request):
    """链接列表"""
    links = Link.objects.filter(is_visible=True)
    
    # 按分类分组
    services = links.filter(category='service')
    external = links.filter(category='external')
    projects = links.filter(category='project')
    
    context = {
        'services': services,
        'external': external,
        'projects': projects,
        'all_links': links,
    }
    return render(request, 'links/list.html', context)
