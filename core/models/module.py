from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel


class Module(BaseModel):
    name = models.CharField("nome", max_length=100, unique=True)
    slug = models.SlugField("slug", max_length=120, unique=True, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    is_core = models.BooleanField(
        "módulo essencial",
        default=False,
        help_text="Módulos core são ativados automaticamente em toda organização nova."
    )
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    class Meta:
        verbose_name = "módulo"
        verbose_name_plural = "módulos"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
