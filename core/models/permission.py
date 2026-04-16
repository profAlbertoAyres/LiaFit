from django.db import models
from core.models.base import BaseModel


class Permission(BaseModel):
    module = models.ForeignKey(
        'core.Module',
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name='Módulo',
    )
    codename = models.CharField('Código', max_length=100)
    name = models.CharField('Nome', max_length=150)

    class Meta:
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
        unique_together = ('module', 'codename')

    def __str__(self):
        return f"{self.module.codename}.{self.codename}"
