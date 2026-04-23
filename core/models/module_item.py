from django.db import models
from core.models.base import BaseModel
from core.models.module import Module


class ModuleItem(BaseModel):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        related_name="items", verbose_name="módulo",
    )
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, blank=True)
    description = models.TextField("descrição", blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    # Rotas especiais que fogem do padrão tenant:<route_base>_<action>
    SPECIAL_MENU_ROUTES = {
        ("account", "organization"): "account:organization_detail",
        ("core", "dashboard"): "core:dashboard",
    }

    class Meta:
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]

    def __str__(self):
        return f"{self.module.name} - {self.name}"

    @property
    def route_base(self) -> str:
        """Base técnica derivada do slug. Ex: 'work-out' → 'workout'."""
        return self.slug.replace("-", "_")

    def url_name(self, action: str = "list") -> str:
        """Nome de URL padrão. Ex: url_name('create') → 'tenant:patient_create'."""
        return f"tenant:{self.route_base}_{action}"

    @property
    def menu_url_name(self) -> str:
        """URL usada no menu lateral (considera rotas especiais)."""
        key = (self.module.slug, self.slug)
        return self.SPECIAL_MENU_ROUTES.get(key, self.url_name("list"))

    def permission_codename(self, action: str = "view") -> str:
        """Codename RBAC. Ex: permission_codename('add') → 'add_patient'."""
        return f"{action}_{self.route_base}"
