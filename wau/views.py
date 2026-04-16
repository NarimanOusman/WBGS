from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

from .models import Project

def projects(request):
    mock_projects = Project.objects.all().prefetch_related('images').order_by('-created_at')
    return render(request, 'projects.html', {'projects': mock_projects})


def project_detail(request, pk):
    project = get_object_or_404(Project.objects.prefetch_related('images'), pk=pk)
    return render(request, 'project_detail.html', {'project': project})
