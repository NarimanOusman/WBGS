from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from .models import NewsPost, Project, ProjectImage, InvestmentOpportunity, InvestmentInquiry


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []

        files = data if isinstance(data, (list, tuple)) else [data]
        cleaned_files = []

        for uploaded in files:
            cleaned_files.append(super().clean(uploaded, initial))

        return cleaned_files


class ProjectAdminForm(forms.ModelForm):
    gallery_images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple gallery images.',
        label='Gallery images',
    )
    before_images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple before images.',
        label='Before images',
    )
    after_images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={'accept': 'image/*'}),
        help_text='Optional: select multiple after images.',
        label='After images',
    )

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'image' in self.fields:
            self.fields['image'].label = 'Cover image'


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
                    '(missing columns like projectimage.image_type or unapplied migration). '
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


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'published_at', 'updated_at')
    list_filter = ('status', 'published_at')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    actions = ('archive_selected_posts', 'restore_selected_posts')
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'summary', 'content', 'cover_image')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except Exception as exc:
            messages.error(
                request,
                (
                    'News save failed. This is usually caused by production storage or database '
                    f'configuration issues. Technical detail: {exc}'
                ),
            )
            return redirect(request.path)

    @admin.action(description='Archive selected news posts')
    def archive_selected_posts(self, request, queryset):
        archived_count = queryset.update(status='archived')
        self.message_user(request, f'{archived_count} news post(s) archived.')

    @admin.action(description='Restore selected archived posts')
    def restore_selected_posts(self, request, queryset):
        restored_count = queryset.filter(status='archived').update(status='published')
        self.message_user(request, f'{restored_count} news post(s) restored to published.')


class InvestmentOpportunityAdminForm(forms.ModelForm):
    class Meta:
        model = InvestmentOpportunity
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Investment Terms guidance
        self.fields['capex_min'].widget.attrs.update({
            'placeholder': 'Minimum capital in USD (e.g., 1000000)',
            'step': '0.01',
        })
        self.fields['capex_max'].widget.attrs.update({
            'placeholder': 'Maximum capital in USD (e.g., 5000000)',
            'step': '0.01',
        })
        self.fields['expected_roi'].widget.attrs.update({
            'placeholder': 'Expected ROI in % (e.g., 18.50)',
            'step': '0.01',
        })
        self.fields['timeline_months'].widget.attrs.update({
            'placeholder': 'Estimated timeline in months (e.g., 24)',
            'min': '1',
        })

        # Opportunity Details guidance
        self.fields['target_sectors'].widget.attrs.update({
            'placeholder': 'Optional: list related sectors (e.g., Agriculture, Logistics, Export)',
        })
        self.fields['key_benefits'].widget.attrs.update({
            'placeholder': 'Summarize top investor benefits (market size, incentives, demand, partners).',
            'rows': 4,
        })

        self.fields['capex_min'].help_text = 'Enter the minimum amount an investor can commit (USD).'
        self.fields['capex_max'].help_text = 'Enter the upper funding target (USD). Must be greater than minimum.'
        self.fields['expected_roi'].help_text = 'Estimated return on investment percentage per project plan.'
        self.fields['timeline_months'].help_text = 'How long project delivery is expected to take.'
        self.fields['target_sectors'].help_text = 'Optional. Comma-separated sectors this opportunity touches.'
        self.fields['key_benefits'].help_text = 'Optional. Why this is attractive to investors.'


@admin.register(InvestmentOpportunity)
class InvestmentOpportunityAdmin(admin.ModelAdmin):
    form = InvestmentOpportunityAdminForm
    list_display = ('title', 'sector', 'status', 'expected_roi', 'featured', 'published_at')
    list_filter = ('status', 'sector', 'featured', 'published_at')
    search_fields = ('title', 'description', 'key_benefits')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    
    fieldsets = (
        ('Opportunity Overview', {
            'fields': ('title', 'sector', 'status', 'featured', 'description')
        }),
        ('Investment Terms', {
            'fields': ('capex_min', 'capex_max', 'expected_roi', 'timeline_months')
        }),
        ('Opportunity Details', {
            'fields': ('target_sectors', 'key_benefits'),
            'classes': ('collapse',),
        }),
        ('Publishing', {
            'fields': ('published_at',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except Exception as exc:
            messages.error(
                request,
                (
                    'Investment opportunity save failed. '
                    f'Technical detail: {exc}'
                ),
            )
            return redirect(request.path)


@admin.register(InvestmentInquiry)
class InvestmentInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'opportunity', 'status', 'email', 'organization', 'created_at')
    list_filter = ('status', 'opportunity', 'created_at')
    search_fields = ('name', 'email', 'organization', 'message')
    readonly_fields = ('created_at', 'updated_at')
    actions = ('mark_contacted', 'mark_interested', 'mark_rejected')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Inquiry Details', {
            'fields': ('opportunity', 'name', 'email', 'phone', 'organization')
        }),
        ('Investment Interest', {
            'fields': ('investment_range', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    @admin.action(description='Mark selected inquiries as contacted')
    def mark_contacted(self, request, queryset):
        updated_count = queryset.update(status='contacted')
        self.message_user(request, f'{updated_count} inquiry(ies) marked as contacted.')
    
    @admin.action(description='Mark selected inquiries as interested')
    def mark_interested(self, request, queryset):
        updated_count = queryset.update(status='interested')
        self.message_user(request, f'{updated_count} inquiry(ies) marked as interested.')
    
    @admin.action(description='Mark selected inquiries as rejected')
    def mark_rejected(self, request, queryset):
        updated_count = queryset.update(status='rejected')
        self.message_user(request, f'{updated_count} inquiry(ies) marked as rejected.')
