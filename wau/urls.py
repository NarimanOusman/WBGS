from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('archive/', views.archive, name='archive'),
    path('investment/', views.investment, name='investment'),
    path('feedback/', views.feedback, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('portal-admin/', views.admin_page, name='admin_page'),
]
