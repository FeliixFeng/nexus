from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.pin_utils import is_pin_verified
from .models import Activity, NowItem
from links.models import Link
from blog.models import Post
from django.utils.text import slugify
import uuid
from django.conf import settings
import json


def _check_auth(request):
    """检查认证：API Key 或 PIN"""
    # API Key 认证（程序化调用）
    api_key = request.headers.get('X-Nexus-Key', '')
    if api_key and api_key == settings.NEXUS_API_KEY:
        return True
    # PIN 认证（浏览器）
    return is_pin_verified(request)


# ─── NowItem CRUD ───────────────────────────────────

@csrf_exempt
@require_POST
def now_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    # 支持 JSON 和 form-encoded
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    text = data.get('text', '').strip()
    icon = data.get('icon', '📌').strip() or '📌'
    if not text:
        return JsonResponse({'success': False, 'error': 'text required'}, status=400)
    item = NowItem.objects.create(
        text=text, icon=icon,
        sort_order=NowItem.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': item.id, 'icon': item.icon, 'text': item.text})


@csrf_exempt
@require_POST
def now_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        item = NowItem.objects.get(pk=pk)
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = data.get('text', '').strip()
    icon = data.get('icon', '').strip()
    if text:
        item.text = text
    if icon:
        item.icon = icon
    item.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def now_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        NowItem.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


@csrf_exempt
@require_POST
def now_complete(request, pk):
    """完成：NowItem → Activity 里程碑"""
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        item = NowItem.objects.get(pk=pk)
    except NowItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    from datetime import date
    today = date.today()
    act = Activity.objects.create(
        text=item.text,
        icon=item.icon,
        date_label=f'{today.year}.{today.month:02d}.{today.day:02d}',
        sort_order=0,
    )
    item.delete()
    return JsonResponse({'success': True, 'id': act.id})


# ─── Activity CRUD ──────────────────────────────────

@csrf_exempt
@require_POST
def activity_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    text = data.get('text', '').strip()
    icon = data.get('icon', '📌').strip() or '📌'
    date_label = data.get('date_label', '').strip()
    if not text or not date_label:
        return JsonResponse({'success': False, 'error': 'text and date_label required'}, status=400)
    act = Activity.objects.create(
        text=text, icon=icon, date_label=date_label,
        sort_order=Activity.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': act.id, 'icon': act.icon, 'text': act.text, 'date_label': act.date_label})


@csrf_exempt
@require_POST
def activity_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        act = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    text = data.get('text', '').strip()
    icon = data.get('icon', '').strip()
    date_label = data.get('date_label', '').strip()
    if text:
        act.text = text
    if icon:
        act.icon = icon
    if date_label:
        act.date_label = date_label
    act.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def activity_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Activity.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Activity.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


# ─── Link CRUD ──────────────────────────────────────

@csrf_exempt
@require_POST
def link_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    if not name or not url:
        return JsonResponse({'success': False, 'error': 'name and url required'}, status=400)
    link = Link.objects.create(
        name=name,
        url=url,
        description=data.get('description', '').strip(),
        icon=data.get('icon', '🔗').strip() or '🔗',
        category=data.get('category', 'external').strip() or 'external',
        sort_order=Link.objects.count() + 1,
    )
    return JsonResponse({'success': True, 'id': link.id, 'name': link.name, 'url': link.url})


@csrf_exempt
@require_POST
def link_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        link = Link.objects.get(pk=pk)
    except Link.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    if data.get('name', '').strip():
        link.name = data['name'].strip()
    if data.get('url', '').strip():
        link.url = data['url'].strip()
    if 'description' in data:
        link.description = data['description'].strip()
    if data.get('icon', '').strip():
        link.icon = data['icon'].strip()
    if data.get('category', '').strip():
        link.category = data['category'].strip()
    link.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def link_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Link.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Link.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


@csrf_exempt
def link_list(request):
    """链接列表（只读，无需认证）"""
    links = Link.objects.filter(is_visible=True).values('id', 'name', 'url', 'description', 'icon', 'category')
    return JsonResponse({'success': True, 'links': list(links)})


# ─── Note (Post) CRUD ──────────────────────────────

@csrf_exempt
def note_list(request):
    """笔记列表（只读，无需认证）"""
    posts = Post.objects.filter(status='published').values('id', 'title', 'slug', 'summary', 'created_at', 'updated_at')
    return JsonResponse({'success': True, 'notes': list(posts)})


@csrf_exempt
@require_POST
def note_create(request):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return JsonResponse({'success': False, 'error': 'title and content required'}, status=400)
    post = Post.objects.create(
        title=title,
        content=content,
        summary=data.get('summary', '').strip()[:500],
        status='published',
    )
    return JsonResponse({'success': True, 'id': post.id, 'title': post.title, 'slug': post.slug})


@csrf_exempt
@require_POST
def note_update(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)
    if data.get('title', '').strip():
        post.title = data['title'].strip()
    if data.get('content', '').strip():
        post.content = data['content'].strip()
    if 'summary' in data:
        post.summary = data['summary'].strip()[:500]
    post.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def note_delete(request, pk):
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)
    try:
        Post.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'not found'}, status=404)


@csrf_exempt
@require_POST
def note_import(request):
    """导入 markdown 文件，支持 multipart/form-data 和 JSON"""
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)

    md_content = ''
    title = ''

    # 文件上传方式
    if request.FILES.get('file'):
        f = request.FILES['file']
        md_content = f.read().decode('utf-8')
        title = f.name.rsplit('.', 1)[0] if '.' in f.name else f.name
    # JSON 方式：直接传 content
    elif request.content_type == 'application/json':
        data = json.loads(request.body)
        md_content = data.get('content', '')
        title = data.get('title', '')
    else:
        data = request.POST
        md_content = data.get('content', '')
        title = data.get('title', '')

    if not md_content.strip():
        return JsonResponse({'success': False, 'error': 'content required'}, status=400)

    # 自动提取标题：取第一个 # 标题
    if not title:
        for line in md_content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                break
    if not title:
        title = 'Untitled'

    # 自动生成摘要
    summary = ''
    for line in md_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('```'):
            summary = line[:500]
            break

    post = Post.objects.create(
        title=title,
        content=md_content,
        summary=summary,
        status='published',
    )
    return JsonResponse({'success': True, 'id': post.id, 'title': post.title, 'slug': post.slug})
