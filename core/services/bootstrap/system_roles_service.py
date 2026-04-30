from __future__ import annotations
from django.db import transaction
from core.constants import ROLES, CATALOG, CRUD
from core.models import (
    Module,
    SystemRole,
)
from core.services.bootstrap.catalog import resolve_permissions


@transaction.atomic
def sync_system_roles(*, verbose: bool = False) -> dict:

    stats = {
        "system_roles_created": 0,
        "system_roles_updated": 0,
        "system_role_permissions_set": 0,
    }

    system_scopes = {Module.Scope.GLOBAL, Module.Scope.SUPERUSER}

    for role_def in ROLES:
        scope = role_def.get("scope", Module.Scope.TENANT)
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