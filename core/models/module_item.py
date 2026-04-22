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
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    class Meta:
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]

    @property
    def route_base(self):
        return self.slug.replace("-", "_")

    @property
    def list_url_name(self):
        return f"tenant:{self.route_base}_list"

    @property
    def create_url_name(self):
        return f"tenant:{self.route_base}_create"

    @property
    def detail_url_name(self):
        return f"tenant:{self.route_base}_detail"

    @property
    def update_url_name(self):
        return f"tenant:{self.route_base}_update"

    @property
    def menu_url_name(self):
        special_routes = {
            ("account", "organization"): "account:organization_detail",
            ("core", "dashboard"): "core:dashboard",
        }
        return special_routes.get((self.module.slug, self.slug), self.list_url_name)

    @property
    def view_permission_codename(self):
        return f"tenant.view_{self.route_base}"

    def __str__(self):
        return f"{self.module.name} - {self.name}"
