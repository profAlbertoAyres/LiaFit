from django.db import models


class RolePermission(models.Model):

    role = models.CharField(max_length=50)

    permission = models.ForeignKey(
        "core.ModulePermission",
        on_delete=models.CASCADE
    )