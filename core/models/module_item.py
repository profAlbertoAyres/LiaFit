import logging

from django.db import models
from django.urls import reverse, NoReverseMatch

from config import settings
from core.constants.permissions import ItemSlug
from core.models.base import BaseModel
from core.models.module import Module

logger = logging.getLogger(__name__)

_SCOPE_NAMESPACE_MAP = {
    Module.Scope.TENANT: "tenant",
    Module.Scope.GLOBAL: "master",
    Module.Scope.SUPERUSER: "saas_admin",
}



class ModuleItem(BaseModel):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE,
        related_name="items", verbose_name="módulo",
    )
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField("slug", max_length=120, choices=ItemSlug.choices)
    description = models.TextField("descrição", blank=True, default="")
    icon = models.CharField("ícone", max_length=50, blank=True, default="")
    order = models.PositiveIntegerField("ordem", default=0)
    is_active = models.BooleanField("ativo", default=True)
    show_in_menu = models.BooleanField("exibir no menu", default=True)

    # ⬇️ NOVO: rota explícita vinda do catálogo
    route = models.CharField(
        "rota (URL name)",
        max_length=120,
        blank=True,
        default="",
        help_text="Ex: 'settings:client_list' ou 'master:billing'. Se vazio, "
                  "cai no fallback derivado do slug.",
    )

    owner = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="owned_items",
        verbose_name="módulo controlador",
        null=True, blank=True,
        help_text=(
            "Módulo que controla a disponibilidade do item para a organização. "
            "Se vazio, o próprio 'module' controla."
        ),
    )

    class Meta:
        verbose_name = "item do módulo"
        verbose_name_plural = "itens do módulo"
        ordering = ["module__order", "module__name", "order", "name"]

    def __str__(self):
        return f"{self.module.name} - {self.name}"

    # ─── Helpers ────────────────────────────────────────────────
    @property
    def route_base(self) -> str:
        return self.slug.replace("-", "_")

    @property
    def controller_module(self) -> Module:
        return self.owner or self.module

    def url_name(self, action: str = "list") -> str:
        namespace = _SCOPE_NAMESPACE_MAP.get(self.module.scope, "master")
        return f"{namespace}:{self.route_base}_{action}"

    def permission_codename(self, action: str = "view") -> str:
        return f"{self.module.slug}.{action}_{self.slug}"

    @property
    def menu_url_name(self) -> str:
        """URL usada no menu. Prioriza self.route, cai no convencional."""
        return self.route or self.url_name("list")

    def get_url(self, *, org_slug: str | None = None) -> str | None:

        url_name = self.menu_url_name
        kwargs_attempts = []

        if org_slug:
            kwargs_attempts.append({"org_slug": org_slug})
        kwargs_attempts.append({})

        for kwargs in kwargs_attempts:
            try:
                return reverse(url_name, kwargs=kwargs)
            except NoReverseMatch:
                continue

        logger.warning(
            "[ModuleItem.get_url] URL '%s' não resolve para item '%s.%s' "
            "(org_slug=%r)",
            url_name, self.module.slug, self.slug, org_slug,
        )
        return "#" if settings.DEBUG else None
