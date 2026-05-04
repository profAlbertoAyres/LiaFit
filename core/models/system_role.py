from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel


class SystemRole(BaseModel):

    class Scope(models.TextChoices):
        GLOBAL = "global", "Global (Cliente)"
        SUPERUSER = "superuser", "Superusuário"

    scope = models.CharField(
        "escopo",
        max_length=20,
        choices=Scope.choices,
        db_index=True,
    )
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    level = models.PositiveIntegerField("nível", default=0)
    is_active = models.BooleanField("ativo", default=True)
    permissions = models.ManyToManyField(
        "core.Permission",
        related_name="system_roles",
        blank=True,
        verbose_name="permissões",
    )

    class Meta:
        verbose_name = "papel do sistema"
        verbose_name_plural = "papéis do sistema"
        ordering = ["scope", "level", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["scope", "slug"],
                name="unique_systemrole_slug_per_scope",
            ),
            models.UniqueConstraint(
                fields=["scope", "name"],
                name="unique_systemrole_name_per_scope",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def has_permission(self, codename: str) -> bool:
        return self.permissions.filter(
            codename=codename,
            is_active=True,
        ).exists()

    def __str__(self):
        return f"[{self.get_scope_display()}] {self.name}"
