import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.db.models import Avg

def home(request):
    return render(request, 'index.html')

from .models import Project, ProjectImage

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


@staff_member_required
def admin_page(request):
    projects = Project.objects.all().order_by('-updated_at')
    return render(
        request,
        'admin.html',
        {
            'projects': projects,
            'cloudinary_cloud_name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', None),
            'cloudinary_upload_preset': getattr(settings, 'CLOUDINARY_UPLOAD_PRESET', None),
        },
    )


@staff_member_required
@require_POST
def upload_media(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON payload.'}, status=400)

    project_id = payload.get('project_id')
    slot = (payload.get('slot') or '').strip().lower()
    media_url = (payload.get('media_url') or '').strip()
    media_type = (payload.get('media_type') or 'image').strip().lower()
    caption = (payload.get('caption') or '').strip()
    order = payload.get('order') or 0

    if not project_id:
        return JsonResponse({'ok': False, 'error': 'Project is required.'}, status=400)

    if not media_url:
        return JsonResponse({'ok': False, 'error': 'Media URL is required.'}, status=400)

    project = get_object_or_404(Project, pk=project_id)

    if slot == 'cover':
        project.cover_media_url = media_url
        project.cover_media_type = 'video' if media_type == 'video' else 'image'
        project.image = None
        project.video = None
        project.save()
        return JsonResponse({'ok': True, 'message': 'Project cover updated.'})

    if slot != 'gallery':
        return JsonResponse({'ok': False, 'error': 'Invalid slot.'}, status=400)

    media_item = ProjectImage.objects.create(
        project=project,
        media_url=media_url,
        media_type='video' if media_type == 'video' else 'image',
        caption=caption,
        order=order,
    )
    media_item.image = None
    media_item.video = None
    media_item.save()

    return JsonResponse({'ok': True, 'message': 'Gallery media uploaded.'})
