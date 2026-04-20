from django.db import models
from django.utils.text import slugify

from core.models.tenant import TenantModel


class Role(TenantModel):
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    level = models.PositiveIntegerField("nível", default=0)
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "papel"
        verbose_name_plural = "papéis"
        ordering = ["level", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_role_name_per_organization",
            ),
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_role_slug_per_organization",
            ),
        ]

    @property
    def permission_codenames(self):
        """Codenames de permissões ativas atribuídas a este Role."""
        from core.models.permission import Permission

        return list(
            Permission.objects
            .filter(
                permission_roles__role=self,
                permission_roles__organization=self.organization,
                is_active=True,
            )
            .values_list("codename", flat=True)
        )

    def has_permission(self, codename: str) -> bool:
        """Verifica se o Role possui uma permissão baseada no codename técnico."""
        from core.models.role_permission import RolePermission

        return RolePermission.objects.filter(
            organization=self.organization,
            role=self,
            permission__codename=codename,
            permission__is_active=True,
        ).exists()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
