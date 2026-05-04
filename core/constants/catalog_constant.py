# core/constants/catalog_constant.py
"""
Catálogo declarativo. Fonte única da estrutura de menu + permissions.
"""
from core.constants.permissions_constant import ModuleSlug, ItemSlug, ActionSlug

# Presets
CRUD = [ActionSlug.VIEW, ActionSlug.ADD, ActionSlug.CHANGE, ActionSlug.DELETE]
RO   = [ActionSlug.VIEW]
RW   = [ActionSlug.VIEW, ActionSlug.CHANGE]
A    = [ActionSlug.ADD]


CATALOG = [
    # ─────────────── MY AREA ───────────────
    {
        "slug": ModuleSlug.MY_AREA,
        "name": "Minha Área",
        "icon": "home",
        "order": 1,
        "scope": "global",
        "is_core": True,
        "is_universal": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": ItemSlug.DASHBOARD,
                "name": "Dashboard",
                "icon": "layout-dashboard",
                "order": 10,
                "route": "dashboard",
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
                "actions": CRUD + [ActionSlug.INVITE],
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
{
                "slug": ItemSlug.SPECIALTY,
                "name": "Especialidades",
                "icon": "graduation-cap",
                "order": 20,
                "route": "saas_admin:specialty_list",
                "show_in_menu": True,
                "actions": CRUD,
            },

            {
                "slug": ItemSlug.USERS_ADMIN,
                "name": "Usuários",
                "icon": "users",
                "order": 20,
                "route": "saas_admin:user_list",
                "show_in_menu": True,
                "actions": CRUD,
            },
        ],
    },
]
