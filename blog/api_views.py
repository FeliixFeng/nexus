from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from nexus_core.api_views import _check_auth
from .models import Post, Tag
import json
import re


@csrf_exempt
def note_list(request):
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
    if not _check_auth(request):
        return JsonResponse({'success': False, 'error': 'unauthorized'}, status=403)

    md_content = ''
    title = ''
    tags = []

    if request.FILES.get('file'):
        f = request.FILES['file']
        md_content = f.read().decode('utf-8')
        title = f.name.rsplit('.', 1)[0] if '.' in f.name else f.name
    elif request.content_type == 'application/json':
        data = json.loads(request.body)
        md_content = data.get('content', '')
        title = data.get('title', '')
        tags = data.get('tags', [])
    else:
        data = request.POST
        md_content = data.get('content', '')
        title = data.get('title', '')
        tags = request.POST.getlist('tags', [])

    if not md_content.strip():
        return JsonResponse({'success': False, 'error': 'content required'}, status=400)

    lines = md_content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('> [[') and stripped.endswith(']]'):
            continue
        line = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', line)
        line = re.sub(r'\[\[([^\]]+)\]\]', r'\1', line)
        cleaned_lines.append(line)
    md_content = '\n'.join(cleaned_lines)

    if not title:
        for line in md_content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                break
    if not title:
        title = 'Untitled'

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

    if tags:
        for tag_name in tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)

    return JsonResponse({'success': True, 'id': post.id, 'title': post.title, 'slug': post.slug})
