"""
Bootstrap do sistema LiaFit.

Fluxos:
  1. sync_system_catalog()         → Modules, Items, Permissions
  2. sync_system_roles()           → SystemRoles (global/superuser)
  3. bootstrap_organization(org)   → Módulos core + Roles tenant + owner role
"""

from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from django.db import IntegrityError, transaction
from django.db.models import Q

from core.constants import DEFAULT_ACTIONS, MODULES, ROLES
from core.models import (
    Module,
    ModuleItem,
    OrganizationModule,
    Permission,
    Role,
    RolePermission,
    SystemRole,
)


# ============================================================
# 1) CATÁLOGO DO SISTEMA
# ============================================================

@transaction.atomic
def sync_system_catalog(*, verbose: bool = False) -> dict:
    """
    Sincroniza Module, ModuleItem e Permission a partir de core.constants.MODULES.
    Resolve `owner_slug` em 2 passadas (1ª cria items, 2ª vincula owner).
    """
    stats = {
        "modules_created": 0,
        "modules_updated": 0,
        "items_created": 0,
        "items_updated": 0,
        "permissions_created": 0,
        "owners_linked": 0,
    }

    # ---- 1ª passada: modules + items + permissions ----
    for mod_def in MODULES:
        module, created = Module.objects.update_or_create(
            slug=mod_def["slug"],
            defaults={
                "name": mod_def["name"],
                "description": mod_def.get("description", ""),
                "order": mod_def.get("order", 0),
                "scope": mod_def.get("scope", Module.Scope.TENANT),
                "is_core": mod_def.get("is_core", False),
                "show_in_menu": mod_def.get("show_in_menu", True),
            },
        )
        stats["modules_created" if created else "modules_updated"] += 1
        if verbose:
            print(f"  [{'+' if created else '~'}] module {module.slug} ({module.scope})")

        for item_def in mod_def.get("items", []):
            item, item_created = ModuleItem.objects.update_or_create(
                module=module,
                slug=item_def["slug"],
                defaults={
                    "name": item_def["name"],
                    "icon": item_def.get("icon", ""),
                    "order": item_def.get("order", 0),
                    "show_in_menu": item_def.get("show_in_menu", True),
                },
            )
            stats["items_created" if item_created else "items_updated"] += 1
            if verbose:
                print(f"      [{'+' if item_created else '~'}] item {item.slug}")

            actions = item_def.get("actions") or DEFAULT_ACTIONS
            actions = list(dict.fromkeys(actions))  # dedup mantendo ordem

            for action in actions:
                codename = item.permission_codename(action)  # ← usa o model (fonte única)
                perm, perm_created = Permission.objects.get_or_create(
                    item=item,
                    action=action,
                    defaults={"codename": codename},
                )
                # garante codename correto mesmo em registros antigos
                if not perm_created and perm.codename != codename:
                    perm.codename = codename
                    perm.save(update_fields=["codename"])

                if perm_created:
                    stats["permissions_created"] += 1
                    if verbose:
                        print(f"          [+] perm {perm.codename}")

    # ---- 2ª passada: resolver owners (item_def["owner_slug"]) ----
    for mod_def in MODULES:
        for item_def in mod_def.get("items", []):
            owner_slug = item_def.get("owner_slug")
            if not owner_slug:
                continue
            try:
                item = ModuleItem.objects.get(
                    module__slug=mod_def["slug"],
                    slug=item_def["slug"],
                )
                owner_module = Module.objects.get(slug=owner_slug)
            except (ModuleItem.DoesNotExist, Module.DoesNotExist):
                if verbose:
                    print(f"      [!] owner não resolvido: {mod_def['slug']}.{item_def['slug']} → {owner_slug}")
                continue

            if item.owner_id != owner_module.id:
                item.owner = owner_module
                item.save(update_fields=["owner"])
                stats["owners_linked"] += 1
                if verbose:
                    print(f"      [→] {item} controlado por {owner_module.slug}")

    return stats


# ============================================================
# RESOLUÇÃO DE PERMISSÕES (compartilhado)
# ============================================================

def _resolve_permissions(spec: Iterable[str], *, scope_filter: str | None = None) -> List[Permission]:
    """
    Resolve specs de permissão em QuerySet de Permission.

    Se `scope_filter` for informado, restringe a permissions cujo
    item.module.scope == scope_filter. Útil pra evitar que um role
    'tenant' receba permissões de módulos 'global'.
    """
    spec = list(spec)
    base_qs = Permission.objects.filter(is_active=True)
    if scope_filter:
        base_qs = base_qs.filter(item__module__scope=scope_filter)

    if "*" in spec:
        return list(base_qs)

    codenames: Set[str] = set()
    module_slugs: Set[str] = set()
    item_keys: Set[Tuple[str, str]] = set()

    for entry in spec:
        if entry.startswith("module:"):
            module_slugs.add(entry.split(":", 1)[1])
        elif entry.startswith("item:"):
            mod_slug, item_slug = entry.split(":", 1)[1].split(".", 1)
            item_keys.add((mod_slug, item_slug))
        else:
            codenames.add(entry)  # codename direto

    filters = Q()
    matched = False

    if codenames:
        filters |= Q(codename__in=codenames)
        matched = True
    if module_slugs:
        filters |= Q(item__module__slug__in=module_slugs)
        matched = True
    if item_keys:
        item_q = Q()
        for mod_slug, item_slug in item_keys:
            item_q |= Q(item__module__slug=mod_slug, item__slug=item_slug)
        filters |= item_q
        matched = True

    if not matched:
        return []

    return list(base_qs.filter(filters).distinct())


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
