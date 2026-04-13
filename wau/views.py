from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

from .models import Project

def projects(request):
    mock_projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects.html', {'projects': mock_projects})
