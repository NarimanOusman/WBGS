from django import forms
from django.conf import settings
from django.contrib import admin

from .models import Project, ProjectImage


def _cloudinary_attrs():
    return {
        'class': 'vTextField cloudinary-url-field',
        'data-cloudinary-cloud-name': getattr(settings, 'CLOUDINARY_CLOUD_NAME', '') or '',
        'data-cloudinary-upload-preset': getattr(settings, 'CLOUDINARY_UPLOAD_PRESET', '') or '',
    }


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        url_field = self.fields.get('cover_media_url')
        if url_field:
            attrs = dict(url_field.widget.attrs)
            attrs.update(_cloudinary_attrs())
            attrs['data-cloudinary-slot'] = 'cover'
            url_field.widget.attrs = attrs
            url_field.help_text = 'Use Upload to Cloudinary below this field, then save.'


class ProjectImageInlineForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        url_field = self.fields.get('media_url')
        if url_field:
            attrs = dict(url_field.widget.attrs)
            attrs.update(_cloudinary_attrs())
            attrs['data-cloudinary-slot'] = 'gallery'
            url_field.widget.attrs = attrs


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    form = ProjectImageInlineForm
    extra = 3
    fields = ('media_url', 'media_type', 'image', 'video', 'caption', 'order', 'created_at')
    readonly_fields = ('created_at',)

    class Media:
        js = ('js/admin-cloudinary-widget.js',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'category', 'status', 'progress', 'cover_media_type', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    fields = ('title', 'category', 'status', 'progress', 'description', 'cover_media_url', 'cover_media_type', 'image', 'video')
    inlines = [ProjectImageInline]

    class Media:
        js = ('js/admin-cloudinary-widget.js',)

    @admin.display(description='Cover')
    def cover_media_type(self, obj):
        if obj.cover_media_url:
            return 'Video' if obj.cover_media_type == 'video' else 'Image'
        return 'Video' if obj.video else 'Image'
