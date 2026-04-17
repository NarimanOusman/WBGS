from django.db.models import Q
from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

from .models import Project


def projects(request):
    all_projects = Project.objects.all().prefetch_related('images')

    search_query = request.GET.get('q', '').strip()
    selected_status = request.GET.get('status', '').strip()

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

    projects_qs = projects_qs.order_by('-created_at')

    status_counts = {
        'Planned': all_projects.filter(Q(title__icontains=search_query) | Q(category__icontains=search_query) | Q(description__icontains=search_query), status='Planned').count() if search_query else all_projects.filter(status='Planned').count(),
        'Ongoing': all_projects.filter(Q(title__icontains=search_query) | Q(category__icontains=search_query) | Q(description__icontains=search_query), status='Ongoing').count() if search_query else all_projects.filter(status='Ongoing').count(),
        'Completed': all_projects.filter(Q(title__icontains=search_query) | Q(category__icontains=search_query) | Q(description__icontains=search_query), status='Completed').count() if search_query else all_projects.filter(status='Completed').count(),
    }

    context = {
        'projects': projects_qs,
        'search_query': search_query,
        'selected_status': selected_status,
        'status_choices': valid_statuses,
        'status_counts': status_counts,
        'has_active_filters': bool(search_query or selected_status),
    }
    return render(request, 'projects.html', context)


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('images'), pk=pk)
    return render(request, 'project_detail.html', {'project': project})
