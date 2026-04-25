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
        perms = _resolve_permissions(
            role_def.get("permissions", []),
            scope_filter=scope,
        )
        system_role.permissions.set(perms)
        stats["system_role_permissions_set"] += len(perms)
        if verbose:
            print(f"      → {len(perms)} permissões vinculadas")

    return stats


# ============================================================
# 3) BOOTSTRAP DE ORGANIZAÇÃO
# ============================================================

@transaction.atomic
def bootstrap_organization(organization, *, verbose: bool = False) -> dict:
    """
    Prepara uma organização nova:
      1. Ativa módulos core (scope=tenant, is_core=True)
      2. Cria Roles tenant padrão com suas permissões
      3. Garante que o owner tenha OrganizationMember com role 'owner'
    """
    stats = {
        "modules_enabled": 0,
        "roles_created": 0,
        "roles_updated": 0,
        "role_permissions_created": 0,
        "owner_role_assigned": False,
    }

    # --- 1) Ativar módulos core do tenant ---
    core_modules = Module.objects.filter(
        is_core=True,
        scope=Module.Scope.TENANT,
    )
    for module in core_modules:
        _, created = OrganizationModule.objects.get_or_create(
            organization=organization,
            module=module,
            defaults={"is_active": True},
        )
        if created:
            stats["modules_enabled"] += 1
            if verbose:
                print(f"  [+] módulo core ativado: {module.slug}")

    # --- 2) Criar/atualizar roles tenant ---
    for role_def in ROLES:
        if role_def.get("scope", "tenant") != "tenant":
            continue

        role, created = Role.objects.update_or_create(
            organization=organization,
            slug=role_def["slug"],
            defaults={
                "name": role_def["name"],
                "description": role_def.get("description", ""),
                "level": role_def.get("level", 0),
            },
        )
        stats["roles_created" if created else "roles_updated"] += 1
        if verbose:
            print(f"  [{'+' if created else '~'}] role {role.slug}")

        # Resolver permissões (só de módulos tenant)
        permissions = _resolve_permissions(
            role_def.get("permissions", []),
            scope_filter="tenant",
        )
        for perm in permissions:
            _, rp_created = RolePermission.objects.get_or_create(
                organization=organization,
                role=role,
                permission=perm,
            )
            if rp_created:
                stats["role_permissions_created"] += 1

        if verbose:
            print(f"      → {len(permissions)} permissões vinculadas")

    # --- 3) Garantir owner como OrganizationMember com role 'owner' ---
    if organization.owner_id:
        from account.models import OrganizationMember

        owner_role = Role.objects.get(organization=organization, slug="owner")
        member, _ = OrganizationMember.objects.get_or_create(
            user=organization.owner,
            organization=organization,
            defaults={"is_active": True},
        )
        if not member.roles.filter(pk=owner_role.pk).exists():
            member.roles.add(owner_role)
            stats["owner_role_assigned"] = True
            if verbose:
                print(f"  [+] role 'owner' atribuída a {organization.owner}")

    return stats