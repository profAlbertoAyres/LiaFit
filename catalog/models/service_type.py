from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel


class ServiceType(BaseModel):

    name = models.CharField("nome", max_length=100, unique=True, help_text="Nome do tipo de serviço (ex: Consulta Nutricional).",)
    slug = models.SlugField("slug", max_length=120, unique=True, blank=True, help_text="Identificador único gerado automaticamente a partir do nome.",)
    description = models.TextField("descrição", blank=True, help_text="Descrição opcional para orientar as organizações.",)
    is_active = models.BooleanField("ativo", default=True, help_text="Indica se o tipo de serviço está disponível para uso.",)

    class Meta:
        verbose_name = "tipo de serviço"
        verbose_name_plural = "tipos de serviço"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)