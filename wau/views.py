from django.db.models import Avg, Q
from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

from .models import Project


def projects(request):
    all_projects = Project.objects.all().prefetch_related('images')

    search_query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_sort = request.GET.get('sort', 'newest').strip()

    valid_statuses = [choice for choice, _ in Project.STATUS_CHOICES]
    if selected_status and selected_status not in valid_statuses:
        selected_status = ''

    projects_qs = all_projects

    if search_query:
        projects_qs = projects_qs.filter(
            Q(title__icontains=search_query)
            | Q(category__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    if selected_status:
        projects_qs = projects_qs.filter(status=selected_status)

    if selected_category:
        projects_qs = projects_qs.filter(category=selected_category)

    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'progress_desc': '-progress',
        'progress_asc': 'progress',
        'title_asc': 'title',
        'title_desc': '-title',
        'status': 'status',
    }
    if selected_sort not in sort_map:
        selected_sort = 'newest'

    projects_qs = projects_qs.order_by(sort_map[selected_sort], '-created_at')

    total_projects = projects_qs.count()
    completed_projects = projects_qs.filter(status='Completed').count()
    ongoing_projects = projects_qs.filter(status='Ongoing').count()
    avg_completion = projects_qs.aggregate(avg=Avg('progress'))['avg'] or 0

    categories = (
        Project.objects.order_by('category')
        .values_list('category', flat=True)
        .distinct()
    )

    context = {
        'projects': projects_qs,
        'filters': {
            'q': search_query,
            'status': selected_status,
            'category': selected_category,
            'sort': selected_sort,
        },
        'status_choices': valid_statuses,
        'category_choices': categories,
        'stats': {
            'total': total_projects,
            'completed': completed_projects,
            'ongoing': ongoing_projects,
            'avg_progress': round(avg_completion),
        },
        'has_active_filters': bool(search_query or selected_status or selected_category),
    }
    return render(request, 'projects.html', context)


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('images'), pk=pk)
    return render(request, 'project_detail.html', {'project': project})
