# core/constants/catalog.py
"""
Catálogo declarativo do sistema. Descreve a ESTRUTURA de menu/permissions.
Os slugs vêm de core.permissions (fonte única da verdade).
"""
from core.constants.permissions import ModuleSlug, ItemSlug, ActionSlug

# Presets de ações
CRUD = [ActionSlug.VIEW, ActionSlug.ADD, ActionSlug.CHANGE, ActionSlug.DELETE]
RO   = [ActionSlug.VIEW]
RW   = [ActionSlug.VIEW, ActionSlug.CHANGE]

# Alias canônico esperado pelo bootstrap
DEFAULT_ACTIONS = CRUD

SYSTEM_CATALOG = [
    # ─────────────── SETTINGS ───────────────
    {
        "slug": ModuleSlug.SETTINGS,
        "name": "Configurações",
        "icon": "settings",
        "order": 20,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.ROLE,
                "name": "Papéis",
                "icon": "shield",
                "order": 10,
                "route": "setting:role_list",
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.MEMBER,
                "name": "Membros",
                "icon": "users",
                "order": 20,
                "route": "setting:member_list",
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.ORGANIZATION,
                "name": "Organização",
                "icon": "building",
                "order": 30,
                "route": "account:organization_detail",
                "actions": RW,
            },
        ],
    },

    # ─────────────── SETTINGS ───────────────
    {
        "slug": ModuleSlug.ACCOUNT,
        "name": "Cadastros",
        "icon": "database",
        "order": 10,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.CLIENT,
                "name": "Clientes",
                "icon": "user",
                "order": 10,
                "route": "account:client_list",
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.COLLABORATOR,
                "name": "Colaboradores",
                "icon": "briefcase",
                "order": 20,
                "route": "account:collaborator_list",
                "actions": CRUD,
            },
        ],
    },

    # ─────────────── MY AREA ───────────────
    {
        "slug": ModuleSlug.MY_AREA,
        "name": "Minha Área",
        "icon": "home",
        "order": 1,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.DASHBOARD,
                "name": "Dashboard",
                "icon": "layout-dashboard",
                "order": 10,
                "route": "my_area:dashboard",
                "actions": RO,
            },
            {
                "slug": ItemSlug.PROFILE,
                "name": "Meu Perfil",
                "icon": "user-circle",
                "order": 20,
                "route": "my_area:profile",
                "actions": RW,
            },
        ],
    },

    # ─────────────── SAAS ADMIN ───────────────
    {
        "slug": ModuleSlug.SAAS_ADMIN,
        "name": "Admin SaaS",
        "icon": "server",
        "order": 100,
        "scope": "superuser",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.ORGANIZATIONS,
                "name": "Organizações",
                "icon": "building-2",
                "order": 10,
                "route": "saas_admin:organization_list",
                "actions": CRUD,
            },
        ],
    },
]

MODULES = SYSTEM_CATALOG
