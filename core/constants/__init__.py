# core/constants/__init__.py
from core.constants.catalog import CATALOG, CRUD, RO, RW
from core.constants.permissions import ModuleSlug, ItemSlug, ActionSlug
from core.constants.roles import ROLES

__all__ = [
    "CATALOG", "CRUD", "RO", "RW",
    "ModuleSlug", "ItemSlug", "ActionSlug",
    "ROLES",
]
