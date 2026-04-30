# core/constants/roles_constant.py
"""
Catálogo declarativo de Roles (papéis).

Estrutura de cada role:
    - slug:        identificador único (string lowercase)
    - name:        nome amigável (exibição)
    - description: descrição curta
    - scope:       "tenant" | "global" | "superuser"
    - level:       inteiro pra hierarquia (maior = mais poder)
    - permissions: "*" (tudo do scope) ou lista de specs:
        • {"module": <slug>}                       → todas actions do módulo
        • {"module": <slug>, "actions": [<act>]}   → actions específicas
        • {"item": (<mod_slug>, <item_slug>)}      → todas actions do item
        • {"item": (<mod>, <item>), "actions": []} → actions específicas do item
        • "<codename>"                             → permission direta por codename
"""
from core.constants import ItemSlug, ActionSlug
from core.constants.catalog_constant import CRUD, RO, RW
from core.constants.permissions_constant import ModuleSlug


ROLES = [
    # ─────────────── TENANT ───────────────
    {
        "slug": "owner",
        "name": "Proprietário",
        "description": "Dono da organização. Acesso total ao tenant.",
        "scope": "tenant",
        "level": 100,
        "permissions": "*",
    },
    {
        "slug": "admin",
        "name": "Administrador",
        "description": "Administrador da organização. Acesso total ao tenant (limitado por hierarquia).",
        "scope": "tenant",
        "level": 80,
        "permissions": "*",
    },
    {
        "slug": "manager",
        "name": "Gestor",
        "description": "Gerencia cadastros; visualiza configurações.",
        "scope": "tenant",
        "level": 50,
        "permissions": [
            {"module": ModuleSlug.MY_AREA},
            {"module": ModuleSlug.ACCOUNT,  "actions": CRUD},
            {"module": ModuleSlug.SETTINGS, "actions": RO},
            {
                "item": (ModuleSlug.SETTINGS, ItemSlug.MEMBER),
                "actions": [ActionSlug.INVITE, ActionSlug.CHANGE],
            },
        ],
    },
    {
        "slug": "member",
        "name": "Membro",
        "description": "Acesso básico ao tenant (apenas Minha Área).",
        "scope": "tenant",
        "level": 10,
        "permissions": [
            {"module": ModuleSlug.MY_AREA, "actions": RO},
        ],
    },

    # ─────────────── SUPERUSER ───────────────
    {
        "slug": "superadmin",
        "name": "Super Administrador",
        "description": "Administrador da plataforma SaaS. Acesso total ao admin.",
        "scope": "superuser",
        "level": 999,
        "permissions": "*",
    },
]
