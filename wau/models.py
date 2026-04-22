from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planned')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    cover_media_type = models.CharField(max_length=20, default='image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.cover_media_type:
            self.cover_media_type = 'image'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('gallery', 'Gallery'),
        ('before', 'Before'),
        ('after', 'After'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPE_CHOICES,
        default='image',
        db_column='media_type',
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.project.title} {self.image_type} image {self.order}'


class NewsPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    summary = models.TextField(max_length=320)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='news/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @classmethod
    def archive_stale_posts(cls, days=90):
        cutoff = timezone.now() - timedelta(days=days)
        return cls.objects.filter(
            status='published',
            published_at__lt=cutoff,
        ).update(status='archived', updated_at=timezone.now())

    def __str__(self):
        return self.title


class InvestmentOpportunity(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]

    SECTOR_CHOICES = [
        ('agriculture', 'Agriculture'),
        ('renewable_energy', 'Renewable Energy'),
        ('infrastructure', 'Infrastructure'),
        ('technology', 'Technology'),
        ('manufacturing', 'Manufacturing'),
        ('tourism', 'Tourism'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('financial_services', 'Financial Services'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    sector = models.CharField(max_length=30, choices=SECTOR_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Investment details
    description = models.TextField(help_text='Detailed description of the investment opportunity')
    capex_min = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Minimum capital required (USD)'
    )
    capex_max = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Maximum capital sought (USD)'
    )
    expected_roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Expected ROI percentage'
    )
    timeline_months = models.IntegerField(
        help_text='Expected project timeline in months'
    )
    
    # Opportunity details
    target_sectors = models.CharField(
        max_length=500,
        blank=True,
        help_text='Comma-separated target sectors or industries'
    )
    key_benefits = models.TextField(
        blank=True,
        help_text='Key benefits and highlights'
    )
    risk_assessment = models.TextField(
        blank=True,
        help_text='Risk factors and mitigation strategies'
    )
    featured = models.BooleanField(
        default=False,
        help_text='Show on investment page hero section'
    )
    
    # Timestamps
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class InvestmentInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('rejected', 'Rejected'),
    ]

    opportunity = models.ForeignKey(
        InvestmentOpportunity,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    
    # Inquiry details
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    investment_range = models.CharField(
        max_length=50,
        blank=True,
        help_text='Indicated capital range (e.g., "1M-5M")'
    )
    message = models.TextField(help_text='Inquiry message or additional questions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.opportunity.title}'
