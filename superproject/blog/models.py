from django.db import models
from django import forms

class Post(models.Model):
    title = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    hidden = models.BooleanField(default=False)

    def get_absolute_url(self) -> str:
        return f"/blog/{self.pk}/"



