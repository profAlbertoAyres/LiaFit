from django.db import models
from core.models.base import BaseModel


class RolePermission(BaseModel):
    role = models.ForeignKey("core.Role", on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey("core.Permission", on_delete=models.CASCADE, related_name="permission_roles")

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.codename} → {self.permission}"
