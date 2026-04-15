from django.db import models


class ModulePermission(models.Model):

    module = models.ForeignKey(
        "management.Module",
        on_delete=models.CASCADE,
        related_name="permissions"
    )

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("module", "code")

    def __str__(self):
        return f"{self.module.code}.{self.code}"