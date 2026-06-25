from django.shortcuts import render
from blog.models import Post, Tag
from django.db.models import Q, Count
from nexus_core.pin_utils import is_pin_verified


def read_page(request):
    """阅读页面：笔记 + RSS 合并"""
    tag_slug = request.GET.get('tag')
    search = request.GET.get('q')

    # 笔记数据
    if tag_slug:
        posts = Post.objects.filter(
            status='published', tags__name=tag_slug
        ).order_by('-created_at')
    else:
        posts = Post.objects.filter(
            status='published'
        ).order_by('-created_at')

    if search:
        posts = posts.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    tags = Tag.objects.annotate(
        post_count=Count('post', filter=Q(post__status='published'))
    ).order_by('-post_count')
    is_editor = is_pin_verified(request)

    # HTMX 请求只返回笔记列表局部
    if request.headers.get('HX-Request'):
        from django.template.loader import render_to_string
        html = render_to_string('nexus_core/_read_notes.html', {
            'posts': posts, 'search': search or '', 'is_editor': is_editor,
        })
        from django.http import HttpResponse
        return HttpResponse(html)

    from config.settings import RSS_FEEDS
    return render(request, 'nexus_core/read.html', {
        'posts': posts,
        'tags': tags,
        'current_tag': tag_slug,
        'search': search or '',
        'is_editor': is_editor,
        'feeds': RSS_FEEDS,
    })
