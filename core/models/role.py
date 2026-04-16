from django.db import models
from core.models.base import BaseModel


class Role(BaseModel):
    name = models.CharField(max_length=50, verbose_name="Nome")
    codename = models.CharField(max_length=50, unique=True, verbose_name="Código")
    level = models.PositiveIntegerField(
        default=0,
        verbose_name="Nível hierárquico",
        help_text="Quanto maior, mais poder. Ex: OWNER=100, ADMIN=80, PROFESSIONAL=50"
    )
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        ordering = ['-level']

    def __str__(self):
        return f"{self.name} ({self.codename})"
