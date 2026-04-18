from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
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
    exclude = ('cover_media_type',)

    def get_inline_instances(self, request, obj=None):
        # On add form, skip gallery inlines to keep payload small and avoid serverless upload failures.
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except Exception as exc:
            messages.error(
                request,
                (
                    'Project save failed. Production database schema is out of sync with code '
                    '(missing cover_* columns or unapplied migration). '
                    f'Technical detail: {exc}'
                ),
            )
            return redirect(request.path)

    class Media:
        js = ('js/admin_project_upload_guard.js',)
