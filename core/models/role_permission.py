from django.db import models
from core.models.tenant import TenantModel


class RolePermission(TenantModel):
    role = models.ForeignKey(
        "core.Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name="Papel"
    )
    permission = models.ForeignKey(
        "core.Permission",
        on_delete=models.CASCADE,
        related_name="permission_roles",
        verbose_name="Permissão"
    )

    class Meta:
        verbose_name = "Permissão do Papel"
        verbose_name_plural = "Permissões do Papel"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "role", "permission"],
                name="unique_role_permission_per_organization"
            )
        ]

    def __str__(self):
        # Olha que legal: Mostra o slug do role e o codename da permissão
        return f"{self.organization} → {self.role.slug} → {self.permission.codename}"
