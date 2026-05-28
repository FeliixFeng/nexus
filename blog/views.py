from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
import markdown
from .models import Post, Tag
from nexus_core.pin_utils import is_pin_verified


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
        'is_editor': is_pin_verified(request),
    }
    return render(request, 'blog/list.html', context)


def post_detail(request, slug):
    """文章详情"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # 渲染 Markdown 内容
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    post.content_html = mark_safe(md.convert(post.content))
    
    # 上一篇/下一篇
    prev_post = None
    next_post = None
    if post.published_at:
        prev_post = Post.objects.filter(status='published', published_at__lt=post.published_at).order_by('-published_at').first()
        next_post = Post.objects.filter(status='published', published_at__gt=post.published_at).order_by('published_at').first()
    
    context = {
        'post': post,
        'prev_post': prev_post,
        'next_post': next_post,
        'is_editor': is_pin_verified(request),
    }
    return render(request, 'blog/detail.html', context)


def post_create(request):
    """新建笔记"""
    if not is_pin_verified(request):
        return redirect('blog:post_list')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        summary = request.POST.get('summary', '').strip()
        tag_names = request.POST.get('tags', '').strip()
        status = request.POST.get('status', 'published')
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        if not title or not content:
            tags = Tag.objects.all()
            return render(request, 'blog/form.html', {
                'error': '标题和内容不能为空',
                'title': title, 'content': content, 'summary': summary,
                'tag_names': tag_names, 'status': status, 'is_pinned': is_pinned,
                'all_tags': tags, 'is_editor': True,
            })
        
        post = Post.objects.create(
            title=title,
            content=content,
            summary=summary,
            status=status,
            is_pinned=is_pinned,
            published_at=timezone.now() if status == 'published' else None,
        )
        
        # 处理标签
        if tag_names:
            for name in tag_names.split(','):
                name = name.strip()
                if name:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)
        
        return redirect('blog:post_detail', slug=post.slug)
    
    return render(request, 'blog/form.html', {
        'all_tags': Tag.objects.all(),
        'is_editor': True,
    })


def post_update(request, slug):
    """编辑笔记"""
    if not is_pin_verified(request):
        return redirect('blog:post_detail', slug=slug)
    
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        summary = request.POST.get('summary', '').strip()
        tag_names = request.POST.get('tags', '').strip()
        status = request.POST.get('status', 'published')
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        if not title or not content:
            return render(request, 'blog/form.html', {
                'post': post, 'error': '标题和内容不能为空',
                'title': title, 'content': content, 'summary': summary,
                'tag_names': tag_names, 'status': status, 'is_pinned': is_pinned,
                'all_tags': Tag.objects.all(), 'is_editor': True,
            })
        
        post.title = title
        post.content = content
        post.summary = summary
        post.status = status
        post.is_pinned = is_pinned
        if status == 'published' and not post.published_at:
            post.published_at = timezone.now()
        post.save()
        
        # 更新标签
        post.tags.clear()
        if tag_names:
            for name in tag_names.split(','):
                name = name.strip()
                if name:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    post.tags.add(tag)
        
        return redirect('blog:post_detail', slug=post.slug)
    
    return render(request, 'blog/form.html', {
        'post': post,
        'title': post.title,
        'content': post.content,
        'summary': post.summary,
        'tag_names': ', '.join(t.name for t in post.tags.all()),
        'status': post.status,
        'is_pinned': post.is_pinned,
        'all_tags': Tag.objects.all(),
        'is_editor': True,
    })


def post_delete(request, slug):
    """删除笔记"""
    if not is_pin_verified(request):
        return redirect('blog:post_detail', slug=slug)
    
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_list')
    
    return render(request, 'blog/confirm_delete.html', {
        'post': post,
        'is_editor': True,
    })
