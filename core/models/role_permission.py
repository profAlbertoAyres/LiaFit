from django.db import models
from core.models.base import BaseModel


class RolePermission(BaseModel):

    role = models.ForeignKey("core.Role", on_delete=models.CASCADE)
    permission = models.ForeignKey("core.Permission", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("role", "permission")