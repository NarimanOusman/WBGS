from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    video = models.FileField(upload_to='projects/videos/', blank=True, null=True)
    cover_media_url = models.URLField(blank=True, null=True)
    cover_media_type = models.CharField(max_length=10, blank=True, default='image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if not any([self.image, self.video, self.cover_media_url]):
            raise ValidationError('Add a cover image, cover video, or cover media URL for each project.')

    @property
    def cover_is_video(self):
        if self.cover_media_url:
            return self.cover_media_type == 'video'
        return bool(self.video)

    @property
    def cover_media_source(self):
        if self.cover_media_url:
            return self.cover_media_url
        if self.video:
            return self.video.url
        if self.image:
            return self.image.url
        return ''

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/', blank=True, null=True)
    video = models.FileField(upload_to='projects/gallery/videos/', blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=10, blank=True, default='image')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def clean(self):
        super().clean()
        if not any([self.image, self.video, self.media_url]):
            raise ValidationError('Add an image, video, or media URL for each gallery item.')

    @property
    def is_video(self):
        if self.media_url:
            return self.media_type == 'video'
        return bool(self.video)

    @property
    def media_source(self):
        if self.media_url:
            return self.media_url
        if self.video:
            return self.video.url
        if self.image:
            return self.image.url
        return ''

    def __str__(self):
        media_type = 'video' if self.is_video else 'image'
        return f'{self.project.title} {media_type} {self.order}'
