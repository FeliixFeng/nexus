from django.shortcuts import render, get_object_or_404
from .models import Post, Tag


def post_list(request):
    """文章列表"""
    posts = Post.objects.filter(status='published')
    tags = Tag.objects.all()
    
    # 标签筛选
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__name=tag_slug)
    
    # 搜索
    search = request.GET.get('q')
    if search:
        posts = posts.filter(title__icontains=search) | posts.filter(content__icontains=search)
    
    context = {
        'posts': posts,
        'tags': tags,
        'current_tag': tag_slug,
        'search': search or '',
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, slug):
    """文章详情"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # 上一篇/下一篇
    prev_post = Post.objects.filter(status='published', published_at__lt=post.published_at).order_by('-published_at').first()
    next_post = Post.objects.filter(status='published', published_at__gt=post.published_at).order_by('published_at').first()
    
    context = {
        'post': post,
        'prev_post': prev_post,
        'next_post': next_post,
    }
    return render(request, 'blog/detail.html', context)
