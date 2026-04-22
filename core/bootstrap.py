"""
Bootstrap do sistema LiaFit.

1. sync_system_catalog() — sincroniza Module, ModuleItem e Permission
2. bootstrap_organization(org) — ativa módulos core, cria roles e vincula permissões
"""

from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from django.db import transaction, IntegrityError

from core.constants import DEFAULT_ACTIONS, MODULES, ROLES
from core.models import (
    Module,
    ModuleItem,
    OrganizationModule,
    Permission,
    Role,
    RolePermission,
)


@transaction.atomic
def sync_system_catalog(*, verbose: bool = False) -> dict:
    """
    Sincroniza o catálogo do sistema a partir de core.constants.MODULES:
      - Cria/atualiza Modules
      - Cria/atualiza ModuleItems
      - Cria Permissions por (item, action)

    Observações:
      - Permission.codename é gerado no save() do model (action_full_key)
      - Lookup de Permission usa (item, action) pois há UNIQUE(item, action)
      - Tratamos corrida com sinais (post_save) via try/except IntegrityError
    """
    stats = {
        "modules_created": 0,
        "modules_updated": 0,
        "items_created": 0,
        "items_updated": 0,
        "permissions_created": 0,
    }

    for mod_def in MODULES:
        module, created = Module.objects.update_or_create(
            slug=mod_def["slug"],
            defaults={
                "name": mod_def["name"],
                "description": mod_def.get("description", ""),
                "order": mod_def.get("order", 0),
                "is_core": mod_def.get("is_core", False),
                "show_in_menu": mod_def.get("show_in_menu", True),
            },
        )
        stats["modules_created" if created else "modules_updated"] += 1
        if verbose:
            print(f"  [{'+' if created else '~'}] module {module.slug}")

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
            # Deduplicar mantendo ordem (evita IntegrityError desnecessária)
            actions = list(dict.fromkeys(actions))

            for action in actions:
                try:
                    perm, perm_created = Permission.objects.get_or_create(
                        item=item,
                        action=action,
                        defaults={
                            "name": f"{item.name} — {action}",
                        },
                    )
                except IntegrityError:
                    # Corrida: outro processo/sinal criou a mesma perm; busca e segue
                    perm = Permission.objects.get(item=item, action=action)
                    perm_created = False

                # Garantir nome atualizado caso tenha mudado o item.name
                expected_name = f"{item.name} — {action}"
                if perm.name != expected_name:
                    perm.name = expected_name
                    perm.save(update_fields=["name"])

                if perm_created:
                    stats["permissions_created"] += 1
                    if verbose:
                        print(f"          [+] perm {perm.codename}")

    return stats


def _resolve_role_permissions(spec: Iterable[str]) -> List[Permission]:
    if "*" in spec:
        return list(Permission.objects.all())

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
            # Assume codename direto
            codenames.add(entry)

    qs = Permission.objects.none()

    if codenames:
        qs = qs | Permission.objects.filter(codename__in=codenames)

    if module_slugs:
        qs = qs | Permission.objects.filter(item__module__slug__in=module_slugs)

    if item_keys:
        from django.db.models import Q
        q = Q()
        for mod_slug, item_slug in item_keys:
            q |= Q(item__module__slug=mod_slug, item__slug=item_slug)
        qs = qs | Permission.objects.filter(q)

    return list(qs.distinct())


@transaction.atomic
def bootstrap_organization(organization, *, verbose: bool = False) -> dict:

    stats = {
        "modules_enabled": 0,
        "roles_created": 0,
        "roles_updated": 0,
        "role_permissions_created": 0,
    }

    # 1) Ativar módulos core
    core_modules = Module.objects.filter(is_core=True)
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

    # 2) Criar/atualizar roles padrão
    for role_def in ROLES:
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

        # 3) Vincular permissões
        permissions = _resolve_role_permissions(role_def.get("permissions", []))
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

    return stats
