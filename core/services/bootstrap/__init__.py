# core/services/bootstrap/__init__.py
"""
API pública do pacote bootstrap.

Funções expostas:
- sync_system_catalog:    sincroniza Module, ModuleItem e Permission
- sync_system_roles:      sincroniza SystemRoles (escopo global)
- bootstrap_organization: ativa módulos core + cria roles + permissions
                          padrões para uma nova Organization
"""

from core.services.bootstrap.catalog import sync_system_catalog
from core.services.bootstrap.system_roles import sync_system_roles
from core.services.bootstrap.organization import bootstrap_organization

__all__ = [
    "sync_system_catalog",
    "sync_system_roles",
    "bootstrap_organization",
]
