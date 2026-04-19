import json

from django.conf import settings
from django.db import DatabaseError
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.utils import timezone

def home(request):
    return render(request, 'index.html')

from .models import NewsPost, Project, ProjectImage


def _cloud_name_from_settings():
    if settings.CLOUDINARY_CLOUD_NAME:
        return settings.CLOUDINARY_CLOUD_NAME

    # Fallback parse from CLOUDINARY_URL: cloudinary://key:secret@cloud_name
    cloudinary_url = (settings.CLOUDINARY_URL or '').strip()
    if '@' in cloudinary_url:
        return cloudinary_url.rsplit('@', 1)[-1].strip()
    return ''


def _asset_name(asset):
    if not isinstance(asset, dict):
        return ''
    public_id = str(asset.get('public_id') or '').strip()
    asset_format = str(asset.get('format') or '').strip()
    if not public_id:
        return ''
    if asset_format:
        return f'{public_id}.{asset_format}'
    return public_id


def _published_news_queryset():
    try:
        return NewsPost.objects.filter(
            status='published',
            published_at__lte=timezone.now(),
        ).order_by('-published_at', '-created_at')
    except DatabaseError:
        return NewsPost.objects.none()

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
    project_images = list(project.images.all())
    gallery_images = [item for item in project_images if item.image_type in {'gallery', 'image'}]
    before_images = [item for item in project_images if item.image_type == 'before']
    after_images = [item for item in project_images if item.image_type == 'after']

    return render(
        request,
        'project_detail.html',
        {
            'project': project,
            'gallery_images': gallery_images,
            'before_images': before_images,
            'after_images': after_images,
        },
    )


def about(request):
    return render(request, 'about.html')


def news(request):
    published_posts = list(_published_news_queryset())

    featured_post = published_posts[0] if published_posts else None
    other_posts = published_posts[1:] if len(published_posts) > 1 else []

    return render(
        request,
        'news.html',
        {
            'featured_post': featured_post,
            'news_posts': other_posts,
            'news_count': len(published_posts),
        },
    )


def news_detail(request, slug):
    try:
        post = get_object_or_404(
            NewsPost,
            slug=slug,
            status='published',
            published_at__lte=timezone.now(),
        )
        related_posts = _published_news_queryset().exclude(pk=post.pk)[:3]
    except DatabaseError as exc:
        raise Http404('News article unavailable.') from exc

    return render(
        request,
        'news_detail.html',
        {
            'post': post,
            'related_posts': related_posts,
        },
    )


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
            'cloudinary_cloud_name': _cloud_name_from_settings(),
            'cloudinary_upload_preset': settings.CLOUDINARY_UPLOAD_PRESET,
        },
    )


@require_POST
def upload_media(request):
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({'ok': False, 'message': 'Invalid JSON payload.'}, status=400)

    action = str(payload.get('action') or '').strip()

    if action == 'create_project':
        title = str(payload.get('title') or '').strip()
        category = str(payload.get('category') or '').strip()
        status = str(payload.get('status') or 'Planned').strip()
        description = str(payload.get('description') or '').strip()
        progress_raw = payload.get('progress', 0)
        cover_asset = payload.get('cover_asset')

        if not title or not category or not description:
            return JsonResponse({'ok': False, 'message': 'Title, category, and description are required.'}, status=400)

        if status not in {'Planned', 'Ongoing', 'Completed'}:
            status = 'Planned'

        try:
            progress = int(progress_raw)
        except (TypeError, ValueError):
            progress = 0
        progress = max(0, min(100, progress))

        cover_name = _asset_name(cover_asset)
        if not cover_name:
            return JsonResponse({'ok': False, 'message': 'Cover image upload is required.'}, status=400)

        project = Project.objects.create(
            title=title,
            category=category,
            status=status,
            progress=progress,
            description=description,
            image=cover_name,
        )

        gallery_assets = payload.get('gallery_assets') or []
        for item in gallery_assets:
            gallery_name = _asset_name(item.get('asset') if isinstance(item, dict) else None)
            if not gallery_name:
                continue
            caption = str(item.get('caption') or '').strip() if isinstance(item, dict) else ''
            order_raw = item.get('order', 0) if isinstance(item, dict) else 0
            try:
                order = int(order_raw)
            except (TypeError, ValueError):
                order = 0

            ProjectImage.objects.create(
                project=project,
                image=gallery_name,
                caption=caption,
                order=max(0, order),
            )

        return JsonResponse(
            {
                'ok': True,
                'message': 'Project created successfully.',
                'project_id': project.pk,
            }
        )

    if action == 'add_media':
        project_id = payload.get('project_id')
        slot = str(payload.get('slot') or 'gallery').strip().lower()
        asset = payload.get('asset')
        caption = str(payload.get('caption') or '').strip()
        order_raw = payload.get('order', 0)

        try:
            project = Project.objects.get(pk=int(project_id))
        except (TypeError, ValueError, Project.DoesNotExist):
            return JsonResponse({'ok': False, 'message': 'Invalid project selected.'}, status=400)

        asset_name = _asset_name(asset)
        if not asset_name:
            return JsonResponse({'ok': False, 'message': 'Uploaded media asset is missing.'}, status=400)

        if slot == 'cover':
            project.image = asset_name
            project.save(update_fields=['image', 'updated_at'])
            return JsonResponse({'ok': True, 'message': 'Cover media updated.'})

        try:
            order = int(order_raw)
        except (TypeError, ValueError):
            order = 0

        ProjectImage.objects.create(
            project=project,
            image=asset_name,
            image_type='after' if slot == 'after' else ('before' if slot == 'before' else 'gallery'),
            caption=caption,
            order=max(0, order),
        )
        return JsonResponse({'ok': True, 'message': 'Gallery media added.'})

    return JsonResponse({'ok': False, 'message': 'Unsupported action.'}, status=400)
