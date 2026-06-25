from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
import markdown
import re
from .models import Post, Tag
from nexus_core.pin_utils import is_pin_verified


def estimate_reading_time(content):
    """估算阅读时长（中文按每分钟300字）"""
    # 去掉 markdown 语法标记
    text = re.sub(r'[#*`\[\]()>!|_\-\n\r]', '', content)
    text = re.sub(r'\s+', '', text)
    char_count = len(text)
    minutes = max(1, round(char_count / 300))
    return minutes

def post_list(request):
    """文章列表"""
    from django.db.models import Q
    
    tag_slug = request.GET.get('tag')
    search = request.GET.get('q')
    
    # 标签筛选
    if tag_slug:
        posts = Post.objects.filter(
            status='published',
            tags__name=tag_slug
        ).order_by('-created_at')
    else:
        posts = Post.objects.filter(
            status='published'
        ).order_by('-created_at')
    
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
    
    tags = Tag.objects.annotate(post_count=Count('post', filter=Q(post__status='published'))).order_by('-post_count')
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
        'reading_time': estimate_reading_time(post.content),
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
