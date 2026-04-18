from django.contrib import admin
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'progress', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    inlines = [ProjectImageInline]

    def get_inline_instances(self, request, obj=None):
        # On add form, skip gallery inlines to keep payload small and avoid serverless upload failures.
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)
