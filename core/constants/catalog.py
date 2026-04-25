# core/constants/catalog.py
"""
Catálogo declarativo. Fonte única da estrutura de menu + permissions.
"""
from core.constants.permissions import ModuleSlug, ItemSlug, ActionSlug

# Presets
CRUD = [ActionSlug.VIEW, ActionSlug.ADD, ActionSlug.CHANGE, ActionSlug.DELETE]
RO   = [ActionSlug.VIEW]
RW   = [ActionSlug.VIEW, ActionSlug.CHANGE]


CATALOG = [
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
                "route": "tenant:dashboard",
                "show_in_menu": True,
                "actions": RO,
            },
            {
                "slug": ItemSlug.PROFILE,
                "name": "Meu Perfil",
                "icon": "user-circle",
                "order": 20,
                "route": "tenant:profile",
                "show_in_menu": True,
                "actions": RW,
            },
        ],
    },

    # ─────────────── ACCOUNT (Cadastros) ───────────────
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
                "route": "tenant:client_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.COLLABORATOR,
                "name": "Colaboradores",
                "icon": "briefcase",
                "order": 20,
                "route": "tenant:collaborator_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
        ],
    },

    # ─────────────── SETTINGS (Configurações) ───────────────
    {
        "slug": ModuleSlug.SETTINGS,
        "name": "Configurações",
        "icon": "settings",
        "order": 90,
        "scope": "tenant",
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.ROLE,
                "name": "Papéis",
                "icon": "shield",
                "order": 10,
                "route": "tenant:role_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.MEMBER,
                "name": "Membros",
                "icon": "users",
                "order": 20,
                "route": "tenant:member_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
            {
                "slug": ItemSlug.ORGANIZATION,
                "name": "Organização",
                "icon": "building",
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
                "show_in_menu": True,
                "actions": CRUD,
            },
        ],
    },
]
