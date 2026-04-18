from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

def home(request):
    return render(request, 'index.html')

from .models import Project

def projects(request):
    projects = list(Project.objects.all().prefetch_related('images').order_by('-created_at'))
    categories = sorted({project.category for project in projects if project.category})
    total_projects = len(projects)
    completed_projects = sum(1 for project in projects if project.status == 'Completed')
    ongoing_projects = sum(1 for project in projects if project.status == 'Ongoing')
    average_progress = round(sum(project.progress for project in projects) / total_projects) if total_projects else 0

    return render(
        request,
        'projects.html',
        {
            'projects': projects,
            'categories': categories,
            'project_stats': {
                'total': total_projects,
                'completed': completed_projects,
                'ongoing': ongoing_projects,
                'average_progress': average_progress,
            },
        },
    )


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('images'), pk=pk)
    return render(request, 'project_detail.html', {'project': project})


def about(request):
    return render(request, 'about.html')


def news(request):
    return render(request, 'news.html')


def archive(request):
    return render(request, 'archive.html')


def investment(request):
    return render(request, 'investment.html')


def feedback(request):
    return render(request, 'feedback.html')


def contact(request):
    return render(request, 'contact.html')


def admin_page(request):
    return render(
        request,
        'admin.html',
        {
            'projects': Project.objects.all().order_by('-created_at'),
        },
    )


@require_POST
def upload_media(request):
    # Placeholder endpoint so admin page upload action doesn't crash with NoReverseMatch.
    return JsonResponse(
        {
            'ok': False,
            'message': 'Upload endpoint is not configured yet.',
        },
        status=501,
    )
