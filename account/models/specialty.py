from django.db import models
from core.models.base import BaseModel

class Specialty(BaseModel):
    name = models.CharField('Nome da Especialidade', max_length=100, unique=True)
    description = models.TextField('Descrição', blank=True)
    is_active = models.BooleanField('Ativa', default=True)

    class Meta:
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
        ordering = ['name']

    def __str__(self):
        return self.name
