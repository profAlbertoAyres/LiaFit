from django.db import models

from core.models import BaseModel


class Module(BaseModel):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    is_core = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['name']

    def __str__(self):
        return self.name
