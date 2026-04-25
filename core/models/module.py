from django.db import models
from django.utils.text import slugify

from core.constants.permissions import ModuleSlug
from core.models.base import BaseModel


class Module(BaseModel):
    class Scope(models.TextChoices):
        SUPERUSER = "superuser", "Superusuário"
        GLOBAL = "global", "Global (Cliente)"
        TENANT = "tenant", "Organização"

    name = models.CharField("nome", max_length=100, unique=True)
    slug = models.SlugField("slug", max_length=120, unique=True, choices=ModuleSlug.choices,)
    description = models.TextField("descrição", blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    scope = models.CharField(
        "escopo",
        max_length=20,
        choices=Scope.choices,
        default=Scope.TENANT,
        help_text="Define em qual contexto o módulo aparece: área admin (superuser), "
                  "área do cliente (global) ou dentro de uma organização (tenant).",
    )
    is_active = models.BooleanField("ativo", default=True)
    is_universal = models.BooleanField(
        "módulo universal",
        default=False,
        help_text=(
            "Permissões deste módulo são INALIENÁVEIS — concedidas "
            "automaticamente a todos os roles e não podem ser revogadas. "
            "Ex: Minha Área (perfil pessoal, dashboard do usuário)."
        ),
    )
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
