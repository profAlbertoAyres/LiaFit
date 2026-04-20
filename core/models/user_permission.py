from django.db import models
from core.models.tenant import TenantModel


class UserPermission(TenantModel):
    class Effect(models.TextChoices):
        ALLOW = "allow", "Permitir"
        DENY = "deny", "Negar"

    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="specific_permissions",
        verbose_name="Usuário"
    )
    permission = models.ForeignKey(
        "core.Permission",
        on_delete=models.CASCADE,
        related_name="user_permissions",
        verbose_name="Permissão"
    )
    effect = models.CharField(
        max_length=10,
        choices=Effect.choices,
        default=Effect.ALLOW,
        verbose_name="Efeito"
    )

    class Meta:
        verbose_name = "Permissão do Usuário"
        verbose_name_plural = "Permissões do Usuário"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user", "permission"],
                name="unique_user_permission_per_organization"
            )
        ]

    def __str__(self):
        return f"{self.organization} → {self.user.email} → {self.permission.codename} [{self.effect}]"
