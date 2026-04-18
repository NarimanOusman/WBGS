from django.contrib import admin
from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ('media_url', 'media_type', 'image', 'video', 'caption', 'order', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'progress', 'cover_media_type', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    fields = ('title', 'category', 'status', 'progress', 'description', 'cover_media_url', 'cover_media_type', 'image', 'video')
    inlines = [ProjectImageInline]

    @admin.display(description='Cover')
    def cover_media_type(self, obj):
        if obj.cover_media_url:
            return 'Video' if obj.cover_media_type == 'video' else 'Image'
        return 'Video' if obj.video else 'Image'
