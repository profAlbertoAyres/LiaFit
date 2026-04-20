from django.db import models
from django.utils.text import slugify

from core.models.base import BaseModel
from core.models.module import Module


class ModuleItem(BaseModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="módulo",
    )
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    url_name = models.CharField("nome da rota", max_length=150, blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    class Meta:
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "name"],
                name="unique_module_item_name",
            ),
            models.UniqueConstraint(
                fields=["module", "slug"],
                name="unique_module_item_slug",
            ),
        ]

    @property
    def codename_prefix(self):
        prefix = f"{self.module.slug}_{self.slug}"
        return prefix.replace("-", "_")

    def create_default_permissions(self):
        from core.models.permission import Permission

        for action in Permission.Action.values:
            Permission.objects.get_or_create(
                item=self,
                action=action,
            )

    def save(self, *args, **kwargs):
        creating = self.pk is None

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        if creating:
            self.create_default_permissions()

    def __str__(self):
        return f"{self.module.name} - {self.name}"
