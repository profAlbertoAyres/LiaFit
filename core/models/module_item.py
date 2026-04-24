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
    owner = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="owned_items",
        verbose_name="módulo controlador",
        null=True,
        blank=True,
        help_text=(
            "Módulo que controla a disponibilidade do item para a organização. "
            "Se vazio, o próprio 'module' controla. "
            "Ex: item 'Fornecedor' aparece em 'Cadastros' mas depende de 'Financeiro'."
        ),
    )

    class Meta:
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]

    def __str__(self):
        return f"{self.module.name} - {self.name}"

    # ---------------------------------------------------------------
    # Helpers técnicos
    # ---------------------------------------------------------------

    @property
    def route_base(self) -> str:
        return self.slug.replace("-", "_")

    @property
    def controller_module(self) -> Module:
        return self.owner or self.module

    def url_name(self, action: str = "list") -> str:
        namespace = "tenant" if self.module.scope == Module.Scope.TENANT else "master"
        return f"{namespace}:{self.route_base}_{action}"

    def permission_codename(self, action: str = "view") -> str:
        return f"{self.module.slug}.{action}_{self.slug}"


    @property
    def menu_url_name(self) -> str:
        from core.constants import SPECIAL_MENU_ROUTES
        key = (self.module.slug, self.slug)
        if key in SPECIAL_MENU_ROUTES:
            return SPECIAL_MENU_ROUTES[key]
        return self.url_name("list")
