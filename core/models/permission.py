from django.db import models


class Permission(models.Model):
    module = models.ForeignKey("core.Module", on_delete=models.CASCADE, related_name="permissions")
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=150)

    class Meta:
        unique_together = ("module", "codename")

    def __str__(self):
        return f"{self.module.slug}.{self.codename}"
