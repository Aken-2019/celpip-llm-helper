from django.db import models
from django.db.models import DateTimeField
from django.utils.functional import cached_property
from datetime import timedelta

# Create your models here.

class Api2dKey(models.Model):
    key = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    @cached_property
    def group(self):
        result = 0
        return result


    @cached_property
    def expired_at(self):
        if self.group == 0:
            return self.created_at + timedelta(days=365)
