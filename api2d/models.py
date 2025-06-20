from django.db import models
from django.db.models import DateTimeField
from django.utils.functional import cached_property
from datetime import timedelta

# Create your models here.


class Api2dGroup2ExpirationMapping(models.Model):
    group = models.CharField(max_length=100, unique=True)
    type_id = models.CharField(max_length=100)
    validate_days = models.IntegerField()

    def __str__(self):
        return f"{self.group} ({self.type_id}) - {self.validate_days} days"


class Api2dKey(models.Model):
    key = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, unique=True)
    group = models.ForeignKey(
        Api2dGroup2ExpirationMapping, on_delete=models.CASCADE, related_name="api_keys"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def save(self, *args, **kwargs):
        # Check if this is a new key and user already has one
        if not self.pk and Api2dKey.objects.filter(user=self.user).exists():
            from django.core.exceptions import ValidationError

            raise ValidationError("This user already has an API key.")

        if not self.expired_at:
            # Convert created_at to datetime if it's a string
            created_at = self.created_at
            if isinstance(created_at, str):
                from django.utils.dateparse import parse_datetime

                created_at = parse_datetime(created_at)
            # Set expired_at based on group's validate_days if not provided
            if not self.expired_at and self.group.validate_days:
                self.expired_at = created_at + timedelta(days=self.group.validate_days)
        return super().save(*args, **kwargs)
