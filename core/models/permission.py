from django.db import models

from core.models.base import BaseModel
from core.models.module_item import ModuleItem


class Permission(BaseModel):
    class Action(models.TextChoices):
        VIEW = "view", "Visualizar"
        ADD = "add", "Adicionar"
        CHANGE = "change", "Alterar"
        DELETE = "delete", "Excluir"

    item = models.ForeignKey(
        ModuleItem,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name="item do módulo",
    )
    action = models.CharField("ação", max_length=20, choices=Action.choices)
    name = models.CharField("nome", max_length=150, blank=True)
    codename = models.CharField("codename", max_length=200, unique=True, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    is_active = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "permissão"
        verbose_name_plural = "permissões"
        ordering = ["item__module__order", "item__order", "action"]
        constraints = [
            models.UniqueConstraint(
                fields=["item", "action"],
                name="unique_permission_item_action",
            ),
        ]

    @property
    def display_name(self):
        return self.name or f"{self.get_action_display()} {self.item.name}"

    def save(self, *args, **kwargs):
        # Sempre regenera o codename a partir do item (fonte única de verdade)
        self.codename = self.item.permission_codename(self.action)

        if not self.name:
            self.name = f"{self.get_action_display()} {self.item.name}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name
