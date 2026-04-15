from django.db import models
from core.models.base import BaseModel
from core.models.module import Module


class OrganizationModule(BaseModel):

    organization = models.ForeignKey(
        'account.Organization',
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name='Organização'
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='organizations'
    )

    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    activated_at = models.DateTimeField(null=True, blank=True, verbose_name='Ativado em')

    class Meta:
        verbose_name = "Módulo da Organização"
        verbose_name_plural = "Módulos da Organização"

        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'module'],
                name='unique_organization_module'
            )
        ]

    def __str__(self):
        return f"{self.organization} - {self.module}"