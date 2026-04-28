# core/constants/__init__.py
from core.constants.catalog import CATALOG, CRUD, RO, RW, A
from core.constants.permissions import ModuleSlug, ItemSlug, ActionSlug, SystemRoleSlug
from core.constants.roles import ROLES

__all__ = [
    "CATALOG", "CRUD", "RO", "RW", "A",
    "ModuleSlug", "ItemSlug", "ActionSlug", "SystemRoleSlug",
    "ROLES",
]
