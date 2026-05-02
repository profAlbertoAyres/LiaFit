# core/models/role_assignment_log.py
from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models.base import BaseModel


class RoleAssignmentLog(BaseModel):
    """
    Auditoria de atribuições/revogações de papéis em membros.
    """

    class Action(models.TextChoices):
        ASSIGN = "assign", "Atribuído"
        REVOKE = "revoke", "Revogado"

    organization = models.ForeignKey(
        "account.Organization",
        on_delete=models.CASCADE,
        related_name="role_assignment_logs",
    )
    membership = models.ForeignKey(
        "account.OrganizationMember",
        on_delete=models.CASCADE,
        related_name="role_assignment_logs",
    )
    role = models.ForeignKey(
        "core.Role",
        on_delete=models.CASCADE,
        related_name="assignment_logs",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="role_assignment_actions",
    )

    undone_at = models.DateTimeField(null=True, blank=True)
    undone_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignment_undos",
    )

    class Meta:
        verbose_name = "Log de Atribuição de Papel"
        verbose_name_plural = "Logs de Atribuição de Papéis"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["membership", "-created_at"]),
            models.Index(fields=["organization", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.role.slug} → {self.membership_id}"

    @property
    def is_undone(self) -> bool:
        return self.undone_at is not None

    def mark_undone(self, user):
        self.undone_at = timezone.now()
        self.undone_by = user
        self.save(update_fields=["undone_at", "undone_by", "updated_at"])
