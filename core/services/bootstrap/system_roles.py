"""
Bootstrap do sistema LiaFit.

Fluxos:
  1. sync_system_catalog()         → Modules, Items, Permissions
  2. sync_system_roles()           → SystemRoles (global/superuser)
  3. bootstrap_organization(org)   → Módulos core + Roles tenant + owner role
"""

from __future__ import annotations


from django.db import IntegrityError, transaction

from core.constants import ROLES, CATALOG, CRUD
from core.models import (
    Module,
    OrganizationModule,
    Role,
    RolePermission,
    SystemRole,
)
from core.services.bootstrap.catalog import resolve_permissions




# ============================================================
# 2) SYSTEM ROLES (global + superuser)
# ============================================================

@transaction.atomic
def sync_system_roles(*, verbose: bool = False) -> dict:
    """
    Cria/atualiza SystemRoles (scope=global ou superuser) a partir de ROLES.
    """
    stats = {
        "system_roles_created": 0,
        "system_roles_updated": 0,
        "system_role_permissions_set": 0,
    }

    system_scopes = {"global", "superuser"}

    for role_def in ROLES:
        scope = role_def.get("scope", "tenant")
        if scope not in system_scopes:
            continue

        system_role, created = SystemRole.objects.update_or_create(
            scope=scope,
            slug=role_def["slug"],
            defaults={
                "name": role_def["name"],
                "description": role_def.get("description", ""),
                "level": role_def.get("level", 0),
            },
        )
        stats["system_roles_created" if created else "system_roles_updated"] += 1
        if verbose:
            print(f"  [{'+' if created else '~'}] system_role [{scope}] {system_role.slug}")

        # Resolve permissões restritas ao próprio scope
        perms = resolve_permissions(
            role_def.get("permissions", []),
            scope_filter=scope,
        )
        system_role.permissions.set(perms)
        stats["system_role_permissions_set"] += len(perms)
        if verbose:
            print(f"      → {len(perms)} permissões vinculadas")

    return stats