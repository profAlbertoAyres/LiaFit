# core/constants/roles.py
"""
Definição dos Roles do sistema (tenant + system).

Scopes:
  - tenant      → Role por organização (Role model)
  - global      → SystemRole multi-tenant (ex: auditor interno)
  - superuser   → SystemRole com acesso total (equipe LiaFit)

Specs de permissions:
  - "*"                     → todas as perms do scope
  - "module:<slug>"         → todas as perms do módulo
  - "item:<mod>.<item>"     → todas as perms do item
  - "<codename_direto>"     → ex: "account.view_client"
"""
from core.constants.permissions import ModuleSlug, ItemSlug


ROLES = [
    # ════════════════════════════════════════════════════
    # TENANT ROLES — criados em cada Organization
    # ════════════════════════════════════════════════════
    {
        "slug": "owner",
        "name": "Proprietário",
        "description": "Dono da organização. Acesso total aos módulos tenant.",
        "scope": "tenant",
        "level": 100,
        "permissions": ["*"],  # todas as perms de módulos scope=tenant
    },
    {
        "slug": "admin",
        "name": "Administrador",
        "description": "Gerencia membros, papéis, cadastros e configurações.",
        "scope": "tenant",
        "level": 80,
        "permissions": [
            f"module:{ModuleSlug.ACCOUNT}",
            f"module:{ModuleSlug.SETTINGS}",
            f"module:{ModuleSlug.MY_AREA}",
        ],
    },
    {
        "slug": "collaborator",
        "name": "Colaborador",
        "description": "Profissional/assistente da organização.",
        "scope": "tenant",
        "level": 40,
        "permissions": [
            f"module:{ModuleSlug.MY_AREA}",
            f"item:{ModuleSlug.ACCOUNT}.{ItemSlug.CLIENT}",
        ],
    },

    # ════════════════════════════════════════════════════
    # SUPERUSER ROLES — equipe interna LiaFit
    # ════════════════════════════════════════════════════
    {
        "slug": "saas-admin",
        "name": "Admin SaaS",
        "description": "Equipe interna com acesso total à administração do SaaS.",
        "scope": "superuser",
        "level": 999,
        "permissions": ["*"],  # todas as perms scope=superuser
    },
]
