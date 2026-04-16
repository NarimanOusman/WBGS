from django.contrib import admin
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'progress', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    inlines = [ProjectImageInline]
