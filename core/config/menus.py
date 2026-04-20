# core/config/menus.py
from django.utils.translation import gettext_lazy as _
from core.menu import MenuItem, MenuGroup, menu_registry

def register_menus():
    # ── 1. MENU DO CLIENTE (Global) ──────
    menu_registry.register(
        MenuGroup(
            label=_("Minha Área"),
            icon="user",
            order=0,
            scope="global",  # <-- Sempre visível
            items=[
                MenuItem(
                    label=_("Dashboard"),
                    url_name="dashboard", # Rota sem slug
                    icon="layout-dashboard",
                ),
                MenuItem(
                    label=_("Minhas Avaliações"),
                    url_name="client:evaluations",
                    icon="activity",
                ),
            ],
        )
    )

    # ── 3. MENU DO DONO DO SISTEMA (Superuser) ───────────
    menu_registry.register(
        MenuGroup(
            label=_("Administração SaaS"),
            icon="settings",
            order=1000,
            scope="superuser", # <-- Só aparece para is_superuser=True
            items=[
                MenuItem(
                    label=_("Todas as Clínicas"),
                    url_name="master:organizations",
                    icon="building",
                ),
                MenuItem(
                    label=_("Faturamento SaaS"),
                    url_name="master:billing",
                    icon="dollar-sign",
                ),
            ],
        )
    )
