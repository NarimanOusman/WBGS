from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from .models import Project, ProjectImage


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class ProjectAdminForm(forms.ModelForm):
    gallery_images = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple gallery images.',
        label='Gallery images',
    )
    before_images = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple before images.',
        label='Before images',
    )
    after_images = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple after images.',
        label='After images',
    )

    class Meta:
        model = Project
        fields = '__all__'


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'image_type', 'caption', 'order')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'category', 'status', 'progress', 'updated_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    inlines = [ProjectImageInline]
    exclude = ('cover_media_type',)
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'category',
                'status',
                'progress',
                'description',
                'image',
                'gallery_images',
                'before_images',
                'after_images',
            )
        }),
    )

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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        gallery_files = request.FILES.getlist('gallery_images')
        before_files = request.FILES.getlist('before_images')
        after_files = request.FILES.getlist('after_images')

        if not gallery_files and not before_files and not after_files:
            return

        next_order = (obj.images.order_by('-order').first().order + 1) if obj.images.exists() else 0

        for uploaded_file in gallery_files:
            ProjectImage.objects.create(
                project=obj,
                image=uploaded_file,
                image_type='gallery',
                order=next_order,
            )
            next_order += 1

        for uploaded_file in before_files:
            ProjectImage.objects.create(
                project=obj,
                image=uploaded_file,
                image_type='before',
                order=next_order,
            )
            next_order += 1

        for uploaded_file in after_files:
            ProjectImage.objects.create(
                project=obj,
                image=uploaded_file,
                image_type='after',
                order=next_order,
            )
            next_order += 1

    class Media:
        js = ('js/admin_project_upload_guard.js',)
