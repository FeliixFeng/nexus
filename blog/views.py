from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
import markdown
from .models import Post, Tag
from nexus_core.pin_utils import is_pin_verified


from django.http import HttpResponse

def post_list(request):
    """文章列表"""
    from django.db.models import Q
    
    tag_slug = request.GET.get('tag')
    search = request.GET.get('q')
    
    # 标签筛选
    if tag_slug:
        if tag_slug == '科技日报':
            posts = Post.objects.filter(
                status='published',
                tags__name='科技日报'
            ).order_by('-created_at')
        else:
            # 其他标签正常筛选
            posts = Post.objects.filter(
                status='published',
                tags__name=tag_slug
            ).order_by('-created_at')
    else:
        # 全部笔记：最新一条日报 + 其他笔记
        latest_daily = Post.objects.filter(
            status='published',
            tags__name='科技日报'
        ).order_by('-created_at').first()
        
        other_posts = Post.objects.filter(
            status='published'
        ).exclude(tags__name='科技日报').order_by('-created_at')
        
        posts = []
        if latest_daily:
            posts.append(latest_daily)
        posts.extend(other_posts)
    
    # 搜索
    if search:
        if isinstance(posts, list):
            post_ids = [p.id for p in posts]
            posts = Post.objects.filter(id__in=post_ids).filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        else:
            posts = posts.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
    
    tags = Tag.objects.all()
    is_editor = is_pin_verified(request)
    
    # HTMX 请求只返回笔记列表局部
    if request.headers.get('HX-Request'):
        return render(request, 'blog/_notes_list.html', {
            'posts': posts,
            'search': search or '',
            'is_editor': is_editor,
        })
    
    context = {
        'posts': posts,
        'tags': tags,
        'current_tag': tag_slug,
        'search': search or '',
        'is_editor': is_editor,
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
