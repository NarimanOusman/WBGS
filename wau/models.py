from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    cover_public_id = models.CharField(max_length=255, blank=True, default='')
    cover_secure_url = models.URLField(blank=True, default='')
    cover_media_type = models.CharField(max_length=20, default='image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.cover_media_type:
            self.cover_media_type = 'image'

        if self.image:
            image_name = str(self.image.name or '')

            if image_name and not self.cover_public_id:
                filename = image_name.rsplit('/', 1)[-1]
                self.cover_public_id = filename.rsplit('.', 1)[0]

            if not self.cover_secure_url:
                try:
                    self.cover_secure_url = self.image.url or ''
                except Exception:
                    self.cover_secure_url = self.cover_secure_url or ''

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f'{self.project.title} image {self.order}'
