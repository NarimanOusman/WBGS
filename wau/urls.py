from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('archive/', views.archive, name='archive'),
    path('investment/', views.investment, name='investment'),
    path('investment/brief/', views.download_investment_brief, name='download_investment_brief'),
    path('feedback/', views.feedback, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('portal-admin/', views.admin_page, name='admin_page'),
    path('upload-media/', views.upload_media, name='upload_media'),
    
    # Favicon route
    path('favicon.ico', views.favicon, name='favicon'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
