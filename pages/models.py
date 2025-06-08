from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text='Used in the URL (e.g., "about-us" for /about-us/)')
    content = models.TextField(help_text='Markdown content for the page')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        indexes = [
            models.Index(fields=['slug'], name='pages_page_slug_idx'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})
