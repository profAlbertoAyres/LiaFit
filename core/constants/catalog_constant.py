# core/constants/catalog_constant.py
"""
Catálogo declarativo. Fonte única da estrutura de menu + permissions.
"""
from django.utils.translation import gettext_lazy as _

from core.constants.permissions_constant import ModuleSlug, ItemSlug, ActionSlug

# Presets
CRUD = [ActionSlug.VIEW, ActionSlug.ADD, ActionSlug.CHANGE, ActionSlug.DELETE]
RO   = [ActionSlug.VIEW]
RW   = [ActionSlug.VIEW, ActionSlug.CHANGE]
A    = [ActionSlug.ADD]


CATALOG = [
    # ─────────────── MY AREA ───────────────
    # {
    #     "slug": ModuleSlug.MY_AREA,
    #     "name": _("Minha Área"),
    #     "icon": "home",
    #     "order": 1,
    #     "scope": "personal",
    #     "is_core": True,
    #     "is_universal": True,
    #     "show_in_menu": True,
    #     "items": [
    #         {
    #             "slug": ItemSlug.DASHBOARD,
    #             "name": _("Dashboard"),
    #             "icon": "layout-dashboard",
    #             "order": 10,
    #             "route": "dashboard",
    #             "show_in_menu": True,
    #             "actions": RO,
    #         },
    #         {
    #             "slug": ItemSlug.PROFILE,
    #             "name": _("Meu Perfil"),
    #             "icon": "user-circle",
    #             "order": 20,
    #             "route": "personal:profile",
    #             "show_in_menu": True,
    #             "actions": RW,
    #         },
    #     ],
    # },

    # ─────────────── ACCOUNT (Cadastros) ───────────────
    {
        "slug": ModuleSlug.ACCOUNT,
        "name": _("Cadastros"),
        "icon": "contact-round",
        "order": 10,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.CLIENT,
                "name": _("Clientes"),
                "order": 10,
                "route": "tenant:client_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
        ],
    },

    # ─────────────── SETTINGS (Configurações) ───────────────
    {
        "slug": ModuleSlug.SETTINGS,
        "name": _("Configurações"),
        "icon": "settings",
        "order": 90,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.ROLE,
                "name": _("Papéis"),
                "order": 10,
                "route": "tenant:role_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.MEMBER,
                "name": _("Membros"),
                "order": 20,
                "route": "tenant:member_list",
                "show_in_menu": True,
                "actions": CRUD + [ActionSlug.INVITE],
            },
            {
                "slug": ItemSlug.ORGANIZATION,
                "name": _("Organização"),
                "order": 30,
                "route": "tenant:organization_detail",
                "show_in_menu": True,
                "actions": RW,
            },
        ],
    },

    # ─────────────── SAAS ADMIN ───────────────
    {
        "slug": ModuleSlug.SAAS_ADMIN,
        "name": _("Admin SaaS"),
        "icon": "shield-check",
        "order": 100,
        "scope": "saas_admin",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.ORGANIZATIONS,
                "name": _("Organizações"),
                "order": 10,
                "route": "saas_admin:organization_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.SPECIALTY,
                "name": _("Especialidades"),
                "order": 20,
                "route": "saas_admin:specialty_list",
                "show_in_menu": True,
                "actions": CRUD,
            },

            {
                "slug": ItemSlug.USERS_ADMIN,
                "name": _("Usuários"),
                "order": 30,
                "route": "saas_admin:user_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
        ],
    },
]
