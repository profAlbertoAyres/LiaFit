# core/constants/__init__.py
from core.constants.catalog import (
    MODULES,
    DEFAULT_ACTIONS,
    CRUD,   # mantém exportado pra compatibilidade
    RO,
    RW,
)
from core.constants.permissions import (
    ModuleSlug,
    ItemSlug,
    ActionSlug,
    PermSet,
    AccountModule,
    SettingsModule,
    MyAreaModule,
    SaasAdminModule,
    ALL_MODULES,
)
from core.constants.roles import ROLES

__all__ = [
    # catalog
    "MODULES", "DEFAULT_ACTIONS", "CRUD", "RO", "RW",
    # permissions
    "ModuleSlug", "ItemSlug", "ActionSlug", "PermSet",
    "AccountModule", "SettingsModule", "MyAreaModule", "SaasAdminModule",
    "ALL_MODULES",
    # roles
    "ROLES",
]
