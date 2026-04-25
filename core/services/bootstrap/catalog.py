from __future__ import annotations

from typing import List


# ============================================================
# 1) CATÁLOGO DO SISTEMA
# ============================================================
from django.db import transaction
from django.db.models import Q

from core.constants import CATALOG, CRUD
from core.models import Module, Permission, ModuleItem


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
    for mod_def in CATALOG:
        module, created = Module.objects.update_or_create(
            slug=mod_def["slug"],
            defaults={
                "name": mod_def["name"],
                "description": mod_def.get("description", ""),
                "order": mod_def.get("order", 0),
                "scope": mod_def.get("scope", Module.Scope.TENANT),
                "is_core": mod_def.get("is_core", False),
                "is_universal": mod_def.get("is_universal", False),  # 🆕
                "show_in_menu": mod_def.get("show_in_menu", True),
            },
        )
        stats["modules_created" if created else "modules_updated"] += 1
        if verbose:
            flags = []
            if module.is_core:
                flags.append("core")
            if module.is_universal:
                flags.append("🌐universal")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            print(f"  [{'+' if created else '~'}] module {module.slug} ({module.scope}){flag_str}")

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

            actions = item_def.get("actions") or CRUD
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
    for mod_def in CATALOG:
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

def resolve_permissions(spec, *, scope_filter: str | None = None) -> List[Permission]:
    """
    Resolve specs de permissão em lista de Permission.

    Formatos aceitos em `spec`:
      • "*"                                          → todas as permissões do scope
      • [ ... lista de entradas ... ]
            "<codename>"                             → permission por codename
            {"module": <slug>}                       → todas actions do módulo
            {"module": <slug>, "actions": [<act>]}   → actions específicas do módulo
            {"item":   (<mod>, <item>)}              → todas actions do item
            {"item":   (<mod>, <item>), "actions": [<act>]}

    Se `scope_filter` for informado, restringe a permissions cujo
    item.module.scope == scope_filter. Evita que um role 'tenant'
    receba permissões de módulos 'global'/'superuser'.
    """
    base_qs = Permission.objects.filter(is_active=True)
    if scope_filter:
        base_qs = base_qs.filter(item__module__scope=scope_filter)

    # Atalho: "*" sozinho ou dentro de lista significa "tudo do scope"
    if spec == "*" or (isinstance(spec, (list, tuple)) and "*" in spec):
        return list(base_qs)

    if not isinstance(spec, (list, tuple)):
        return []

    filters = Q()
    matched = False

    for entry in spec:
        # ─── 1) String → codename direto ───
        if isinstance(entry, str):
            filters |= Q(codename=entry)
            matched = True
            continue

        # ─── 2) Dict → module/item + actions opcionais ───
        if isinstance(entry, dict):
            actions = entry.get("actions")  # None = todas

            # 2a) Por módulo
            if "module" in entry:
                mod_slug = str(entry["module"])  # aceita TextChoices ou str
                q = Q(item__module__slug=mod_slug)
                if actions:
                    q &= Q(action__in=[str(a) for a in actions])
                filters |= q
                matched = True
                continue

            # 2b) Por item (tupla mod_slug, item_slug)
            if "item" in entry:
                mod_slug, item_slug = entry["item"]
                q = Q(
                    item__module__slug=str(mod_slug),
                    item__slug=str(item_slug),
                )
                if actions:
                    q &= Q(action__in=[str(a) for a in actions])
                filters |= q
                matched = True
                continue

    if not matched:
        return []

    return list(base_qs.filter(filters).distinct())
