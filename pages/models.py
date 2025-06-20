from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Model for displaying site-wide notifications."""

    MESSAGE_TYPES = [
        ("info", "Information"),
        ("success", "Success"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ]

    title = models.CharField(max_length=200, help_text="Notification title (optional)")
    message = models.TextField(help_text="The notification message to display")
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default="info",
        help_text="Determines the notification style",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this notification should be displayed"
    )
    start_date = models.DateTimeField(
        default=timezone.now, help_text="When the notification should start appearing"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification should stop appearing (leave blank for no end date)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        indexes = [
            models.Index(fields=["is_active", "start_date", "end_date"]),
        ]

    def __str__(self):
        return (
            f"{self.get_message_type_display()}: {self.title or self.message[:50]}..."
        )

    def is_currently_active(self):
        """Check if the notification should be displayed now."""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    @property
    def css_class(self):
        """Get the appropriate CSS class for the notification."""
        return {
            "info": "alert-info",
            "success": "alert-success",
            "warning": "alert-warning",
            "danger": "alert-danger",
        }.get(self.message_type, "alert-info")


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text='Used in the URL (e.g., "about-us" for /about-us/)',
    )
    content = models.TextField(help_text="Markdown content for the page")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        indexes = [
            models.Index(fields=["slug"], name="pages_page_slug_idx"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("pages:page_detail", kwargs={"slug": self.slug})
