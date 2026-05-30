from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Paper, Experiment
from nexus_core.pin_utils import is_pin_verified


def paper_list(request):
    """论文列表"""
    status_filter = request.GET.get('status')
    search = request.GET.get('q')

    papers = Paper.objects.all()
    if status_filter:
        papers = papers.filter(status=status_filter)
    if search:
        from django.db.models import Q
        papers = papers.filter(
            Q(title__icontains=search) |
            Q(authors__icontains=search) |
            Q(takeaway__icontains=search) |
            Q(tags__icontains=search)
        )

    # HTMX 局部返回
    if request.headers.get('HX-Request'):
        return render(request, 'research/_paper_list.html', {
            'papers': papers,
            'is_editor': is_pin_verified(request),
        })

    return render(request, 'research/papers.html', {
        'papers': papers,
        'status_filter': status_filter,
        'search': search or '',
        'is_editor': is_pin_verified(request),
    })


def paper_detail(request, pk):
    """论文详情"""
    paper = get_object_or_404(Paper, pk=pk)
    experiments = paper.experiments.all()
    return render(request, 'research/paper_detail.html', {
        'paper': paper,
        'experiments': experiments,
        'is_editor': is_pin_verified(request),
    })


@require_POST
def paper_create(request):
    """创建论文"""
    if not is_pin_verified(request):
        return JsonResponse({'error': '未授权'}, status=403)

    paper = Paper.objects.create(
        title=request.POST.get('title', '').strip(),
        authors=request.POST.get('authors', '').strip(),
        doi=request.POST.get('doi', '').strip(),
        url=request.POST.get('url', '').strip(),
        venue=request.POST.get('venue', '').strip(),
        year=int(request.POST['year']) if request.POST.get('year') else None,
        takeaway=request.POST.get('takeaway', '').strip(),
        notes=request.POST.get('notes', '').strip(),
        status=request.POST.get('status', 'unread'),
        tags=request.POST.get('tags', '').strip(),
        rating=int(request.POST['rating']) if request.POST.get('rating') else None,
    )
    return redirect('research:paper_detail', pk=paper.pk)


@require_POST
def paper_update(request, pk):
    """更新论文"""
    if not is_pin_verified(request):
        return JsonResponse({'error': '未授权'}, status=403)

    paper = get_object_or_404(Paper, pk=pk)
    paper.title = request.POST.get('title', paper.title).strip()
    paper.authors = request.POST.get('authors', paper.authors).strip()
    paper.doi = request.POST.get('doi', paper.doi).strip()
    paper.url = request.POST.get('url', paper.url).strip()
    paper.venue = request.POST.get('venue', paper.venue).strip()
    paper.year = int(request.POST['year']) if request.POST.get('year') else paper.year
    paper.takeaway = request.POST.get('takeaway', paper.takeaway).strip()
    paper.notes = request.POST.get('notes', paper.notes).strip()
    paper.status = request.POST.get('status', paper.status)
    paper.tags = request.POST.get('tags', paper.tags).strip()
    paper.rating = int(request.POST['rating']) if request.POST.get('rating') else paper.rating
    paper.save()
    return redirect('research:paper_detail', pk=paper.pk)


@require_POST
def paper_delete(request, pk):
    """删除论文"""
    if not is_pin_verified(request):
        return JsonResponse({'error': '未授权'}, status=403)
    paper = get_object_or_404(Paper, pk=pk)
    paper.delete()
    return redirect('research:paper_list')


def experiment_list(request):
    """实验日志列表"""
    experiments = Experiment.objects.select_related('paper').all()
    search = request.GET.get('q')
    if search:
        from django.db.models import Q
        experiments = experiments.filter(
            Q(name__icontains=search) |
            Q(model_name__icontains=search) |
            Q(dataset__icontains=search)
        )

    if request.headers.get('HX-Request'):
        return render(request, 'research/_experiment_list.html', {
            'experiments': experiments,
            'is_editor': is_pin_verified(request),
        })

    return render(request, 'research/experiments.html', {
        'experiments': experiments,
        'search': search or '',
        'is_editor': is_pin_verified(request),
    })


@require_POST
def experiment_create(request):
    """创建实验"""
    if not is_pin_verified(request):
        return JsonResponse({'error': '未授权'}, status=403)

    paper_id = request.POST.get('paper_id')
    exp = Experiment.objects.create(
        name=request.POST.get('name', '').strip(),
        paper_id=int(paper_id) if paper_id else None,
        model_name=request.POST.get('model_name', '').strip(),
        params=request.POST.get('params', '').strip(),
        metrics=request.POST.get('metrics', '').strip(),
        dataset=request.POST.get('dataset', '').strip(),
        notes=request.POST.get('notes', '').strip(),
        gpu_hours=float(request.POST['gpu_hours']) if request.POST.get('gpu_hours') else None,
        checkpoint=request.POST.get('checkpoint', '').strip(),
    )

    if request.headers.get('HX-Request'):
        return render(request, 'research/_experiment_row.html', {'exp': exp, 'is_editor': True})
    return redirect('research:experiment_list')


@require_POST
def experiment_delete(request, pk):
    """删除实验"""
    if not is_pin_verified(request):
        return JsonResponse({'error': '未授权'}, status=403)
    exp = get_object_or_404(Experiment, pk=pk)
    exp.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    return redirect('research:experiment_list')


def research_home(request):
    """学术模块首页"""
    papers_count = Paper.objects.count()
    reading_count = Paper.objects.filter(status='reading').count()
    finished_count = Paper.objects.filter(status='finished').count()
    experiments_count = Experiment.objects.count()
    recent_papers = Paper.objects.all()[:5]
    recent_experiments = Experiment.objects.select_related('paper').all()[:5]

    return render(request, 'research/home.html', {
        'papers_count': papers_count,
        'reading_count': reading_count,
        'finished_count': finished_count,
        'experiments_count': experiments_count,
        'recent_papers': recent_papers,
        'recent_experiments': recent_experiments,
        'is_editor': is_pin_verified(request),
    })
