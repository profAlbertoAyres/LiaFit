from django.conf import settings
from django.db import models

from core.models.base import BaseModel


class UserSystemRole(BaseModel):
    """
    Atribuição de um SystemRole a um usuário.

    Não usamos M2M direto em User.system_roles pra manter
    timestamps (created_at, updated_at) e espaço pra campos
    futuros (ex: granted_by, expires_at).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="system_roles",
        verbose_name="usuário",
    )
    system_role = models.ForeignKey(
        "core.SystemRole",
        on_delete=models.CASCADE,
        related_name="user_assignments",
        verbose_name="papel do sistema",
    )
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "papel do sistema do usuário"
        verbose_name_plural = "papéis do sistema dos usuários"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "system_role"],
                name="unique_user_system_role",
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.system_role}"
