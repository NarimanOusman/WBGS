import json
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone


logger = logging.getLogger(__name__)

from .models import NewsPost, Project, ProjectImage, InvestmentOpportunity, InvestmentInquiry
from .utils import get_investment_brief_file_response


def _render_projects_dashboard(request):
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


def home(request):
    return _render_projects_dashboard(request)


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


def _archived_news_queryset():
    try:
        return NewsPost.objects.filter(status='archived').order_by('-published_at', '-updated_at')
    except DatabaseError:
        return NewsPost.objects.none()


def _run_news_archiver():
    try:
        return NewsPost.archive_stale_posts(getattr(settings, 'NEWS_ARCHIVE_AFTER_DAYS', 90))
    except Exception:
        logger.exception('Automatic news archiving failed')
        return 0

def projects(request):
    return redirect('home', permanent=True)


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
    try:
        _run_news_archiver()
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
                'archive_days': getattr(settings, 'NEWS_ARCHIVE_AFTER_DAYS', 90),
            },
        )
    except Exception:
        logger.exception('News page failed to render')
        return render(
            request,
            'news.html',
            {
                'featured_post': None,
                'news_posts': [],
                'news_count': 0,
                'archive_days': getattr(settings, 'NEWS_ARCHIVE_AFTER_DAYS', 90),
            },
        )


def news_detail(request, slug):
    try:
        post = get_object_or_404(
            NewsPost,
            slug=slug,
            status__in=['published', 'archived'],
            published_at__lte=timezone.now(),
        )
        related_posts = _published_news_queryset().exclude(pk=post.pk)[:3]
    except DatabaseError as exc:
        raise Http404('News article unavailable.') from exc
    except Exception:
        logger.exception('News detail failed to render for slug=%s', slug)
        raise Http404('News article unavailable.')

    return render(
        request,
        'news_detail.html',
        {
            'post': post,
            'related_posts': related_posts,
        },
    )


def archive(request):
    query = str(request.GET.get('q') or '').strip()
    scope = str(request.GET.get('scope') or 'all').strip().lower()
    if scope not in {'all', 'projects', 'news'}:
        scope = 'all'

    selected_category = str(request.GET.get('category') or 'all').strip()
    sort = str(request.GET.get('sort') or 'newest').strip().lower()
    if sort not in {'newest', 'oldest'}:
        sort = 'newest'

    projects_page_number = request.GET.get('projects_page', 1)
    news_page_number = request.GET.get('news_page', 1)

    def build_query(**updates):
        params = request.GET.copy()
        for key, value in updates.items():
            if value is None:
                params.pop(key, None)
            else:
                params[key] = str(value)
        encoded = urlencode(params, doseq=True)
        return f'?{encoded}' if encoded else ''

    def build_page_links(page_obj, page_key, sibling_key, sibling_page):
        if not page_obj or page_obj.paginator.num_pages <= 1:
            return []

        total = page_obj.paginator.num_pages
        current = page_obj.number
        visible_pages = {1, total, current - 1, current, current + 1}
        visible_pages = sorted(page for page in visible_pages if 1 <= page <= total)

        links = []
        previous_page = None
        for page_number in visible_pages:
            if previous_page is not None and page_number - previous_page > 1:
                links.append({'is_ellipsis': True, 'label': '...'} )

            links.append(
                {
                    'is_ellipsis': False,
                    'number': page_number,
                    'is_current': page_number == current,
                    'url': build_query(**{page_key: page_number, sibling_key: sibling_page}),
                }
            )
            previous_page = page_number

        return links

    try:
        _run_news_archiver()
        archived_posts_qs = _archived_news_queryset()
        completed_projects_qs = Project.objects.filter(status='Completed')

        project_categories = sorted(
            {
                category
                for category in Project.objects.filter(status='Completed').values_list('category', flat=True)
                if category
            }
        )

        if selected_category.lower() != 'all':
            completed_projects_qs = completed_projects_qs.filter(category__iexact=selected_category)

        if query:
            archived_posts_qs = archived_posts_qs.filter(
                Q(title__icontains=query)
                | Q(summary__icontains=query)
                | Q(content__icontains=query)
            )
            completed_projects_qs = completed_projects_qs.filter(
                Q(title__icontains=query)
                | Q(category__icontains=query)
                | Q(description__icontains=query)
            )

        if sort == 'oldest':
            archived_posts_qs = archived_posts_qs.order_by('published_at', 'updated_at')
            completed_projects_qs = completed_projects_qs.order_by('updated_at', 'created_at')
        else:
            archived_posts_qs = archived_posts_qs.order_by('-published_at', '-updated_at')
            completed_projects_qs = completed_projects_qs.order_by('-updated_at', '-created_at')

        if scope == 'projects':
            archived_posts_qs = archived_posts_qs.none()
        elif scope == 'news':
            completed_projects_qs = completed_projects_qs.none()

        archive_count = archived_posts_qs.count()
        completed_count = completed_projects_qs.count()

        projects_paginator = Paginator(completed_projects_qs, 6)
        news_paginator = Paginator(archived_posts_qs, 6)

        completed_projects_page = projects_paginator.get_page(projects_page_number)
        archived_news_page = news_paginator.get_page(news_page_number)

        projects_page_links = build_page_links(
            completed_projects_page,
            page_key='projects_page',
            sibling_key='news_page',
            sibling_page=archived_news_page.number,
        )
        news_page_links = build_page_links(
            archived_news_page,
            page_key='news_page',
            sibling_key='projects_page',
            sibling_page=completed_projects_page.number,
        )

        completed_projects = list(completed_projects_page.object_list)
        archived_posts = list(archived_news_page.object_list)
    except Exception:
        logger.exception('Archive page failed to render')
        archived_posts = []
        completed_projects = []
        project_categories = []
        archive_count = 0
        completed_count = 0
        completed_projects_page = None
        archived_news_page = None
        projects_page_links = []
        news_page_links = []

    return render(
        request,
        'archive.html',
        {
            'archived_posts': archived_posts,
            'completed_projects': completed_projects,
            'archive_count': archive_count,
            'completed_count': completed_count,
            'archive_days': getattr(settings, 'NEWS_ARCHIVE_AFTER_DAYS', 90),
            'archive_query': query,
            'archive_scope': scope,
            'archive_category': selected_category,
            'archive_sort': sort,
            'project_categories': project_categories,
            'completed_projects_page': completed_projects_page,
            'archived_news_page': archived_news_page,
            'projects_prev_link': build_query(projects_page=completed_projects_page.previous_page_number(), news_page=archived_news_page.number) if completed_projects_page and completed_projects_page.has_previous() and archived_news_page else '',
            'projects_next_link': build_query(projects_page=completed_projects_page.next_page_number(), news_page=archived_news_page.number) if completed_projects_page and completed_projects_page.has_next() and archived_news_page else '',
            'news_prev_link': build_query(news_page=archived_news_page.previous_page_number(), projects_page=completed_projects_page.number) if archived_news_page and archived_news_page.has_previous() and completed_projects_page else '',
            'news_next_link': build_query(news_page=archived_news_page.next_page_number(), projects_page=completed_projects_page.number) if archived_news_page and archived_news_page.has_next() and completed_projects_page else '',
            'projects_page_links': projects_page_links,
            'news_page_links': news_page_links,
        },
    )


def investment(request):
    try:
        # Handle inquiry form submission
        form_message = None
        form_success = False
    
        if request.method == 'POST':
            try:
                opportunity_id = request.POST.get('opportunity_id')
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                phone = request.POST.get('phone', '').strip()
                organization = request.POST.get('organization', '').strip()
                investment_range = request.POST.get('investment_range', '').strip()
                message = request.POST.get('message', '').strip()
            
                if not all([opportunity_id, name, email, message]):
                    form_message = 'Please fill in all required fields (marked with *).'
                    form_success = False
                else:
                    try:
                        opportunity = InvestmentOpportunity.objects.get(
                            id=opportunity_id,
                            status='published'
                        )
                        inquiry = InvestmentInquiry.objects.create(
                            opportunity=opportunity,
                            name=name,
                            email=email,
                            phone=phone,
                            organization=organization,
                            investment_range=investment_range,
                            message=message,
                            status='new'
                        )
                    
                        # Send email notification to admin
                        try:
                            admin_email = getattr(settings, 'INVESTMENT_ADMIN_EMAIL', 'investment@waustate.gov')
                            admin_subject = f'New Investment Inquiry: {opportunity.title}'
                            admin_message = f'''New investment inquiry received:

Opportunity: {opportunity.title}
Sector: {opportunity.get_sector_display()}

Investor Information:
Name: {name}
Email: {email}
Phone: {phone}
Organization: {organization}
Investment Range: {investment_range}

Message:
{message}

---
View inquiry in admin: /portal-admin/
Status: {inquiry.status}
Created: {inquiry.created_at.strftime('%B %d, %Y at %H:%M')}
'''
                            send_mail(
                                admin_subject,
                                admin_message,
                                settings.DEFAULT_FROM_EMAIL,
                                [admin_email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            logger.warning(f'Failed to send admin notification email: {e}')
                    
                        # Send confirmation email to investor
                        try:
                            investor_subject = f'Investment Inquiry Received - {opportunity.title}'
                            investor_message = f'''Dear {name},

Thank you for your interest in the {opportunity.title} investment opportunity in Western Bahr el Ghazal State.

We have received your inquiry and will review your information carefully. Our investment team will contact you within 24-48 hours to discuss the opportunity in detail.

Opportunity Details:
Title: {opportunity.title}
Sector: {opportunity.get_sector_display()}
Expected ROI: {opportunity.expected_roi}%
Capital Range: ${opportunity.capex_min}M - ${opportunity.capex_max}M USD
Timeline: {opportunity.timeline_months} months

We look forward to exploring this partnership with you.

Best regards,
WAU State Investment Team
investment@waustate.gov
'''
                            send_mail(
                                investor_subject,
                                investor_message,
                                settings.DEFAULT_FROM_EMAIL,
                                [email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            logger.warning(f'Failed to send investor confirmation email: {e}')
                    
                        form_message = f'Thank you, {name}! We received your inquiry and will be in touch within 24-48 hours.'
                        form_success = True
                    except InvestmentOpportunity.DoesNotExist:
                        form_message = 'The selected opportunity could not be found or is no longer available.'
                        form_success = False
            except Exception as e:
                logger.error(f'Investment inquiry submission error: {e}')
                form_message = 'An error occurred while submitting your inquiry. Please try again.'
                form_success = False
    
        # Defaults allow the page to render even if the investment tables are unavailable.
        featured_opportunities = []
        opportunities = []
        sectors = [(choice[0], choice[1]) for choice in InvestmentOpportunity.SECTOR_CHOICES]
        selected_sector = request.GET.get('sector', '')
        search_query = request.GET.get('q', '').strip()

        try:
            featured_opportunities = list(
                InvestmentOpportunity.objects.filter(
                    status='published',
                    featured=True,
                ).order_by('-published_at')[:3]
            )

            opportunities_qs = InvestmentOpportunity.objects.filter(status='published')

            if selected_sector:
                opportunities_qs = opportunities_qs.filter(sector=selected_sector)

            if search_query:
                opportunities_qs = opportunities_qs.filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                    | Q(key_benefits__icontains=search_query)
                )

            opportunities = list(opportunities_qs.order_by('-featured', '-published_at'))
        except DatabaseError as e:
            logger.error(f'Investment page data load failed: {e}')
            if not form_message:
                form_message = 'Investment opportunities are temporarily unavailable. Please check back shortly.'
                form_success = False

        # Pagination (6 opportunities per page)
        paginator = Paginator(opportunities, 6)
        page_num = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page_num)
        except Exception:
            page_obj = paginator.page(1)
    
        context = {
            'featured_opportunities': featured_opportunities,
            'page_obj': page_obj,
            'opportunities': page_obj.object_list,
            'sectors': sectors,
            'selected_sector': selected_sector,
            'search_query': search_query,
            'form_message': form_message,
            'form_success': form_success,
        }

        return render(request, 'investment.html', context)
    except Exception as e:
        logger.error(f'Investment page unexpected error: {e}')
        empty_page = Paginator([], 6).page(1)
        return render(
            request,
            'investment.html',
            {
                'featured_opportunities': [],
                'page_obj': empty_page,
                'opportunities': empty_page.object_list,
                'sectors': [(choice[0], choice[1]) for choice in InvestmentOpportunity.SECTOR_CHOICES],
                'selected_sector': '',
                'search_query': '',
                'form_message': 'Investment opportunities are temporarily unavailable. Please try again shortly.',
                'form_success': False,
            },
        )


def download_investment_brief(request):
    """Download investment brief PDF."""
    try:
        return get_investment_brief_file_response()
    except Exception as e:
        logger.error(f'Investment brief download error: {e}')
        return redirect('investment')


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


def favicon(request):
    """Serve favicon.ico by redirecting to static logo."""
    return redirect(settings.STATIC_URL + 'images/waulogo.webp', permanent=True)
