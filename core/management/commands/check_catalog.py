# core/management/commands/check_catalog.py
"""
Valida a coerência entre o catálogo declarativo e o banco de dados.

Uso:
    python manage.py check_catalog

Sai com código 0 se tudo OK, 1 se houver divergências.
"""
import sys
from django.core.management.base import BaseCommand

from core.constants.catalog import SYSTEM_CATALOG
from core.permissions import ModuleSlug, ItemSlug
from core.models import Module, ModuleItem, Permission


class Command(BaseCommand):
    help = "Valida a coerência entre catalog.py, permissions.py e o banco."

    def handle(self, *args, **opts):
        errors, warnings = [], []

        # ══════ 1. Catálogo x permissions.py (slugs declarados?) ══════
        valid_modules = {str(v) for v in ModuleSlug.values}
        valid_items = {str(v) for v in ItemSlug.values}

        catalog_modules, catalog_items, catalog_perms = set(), set(), set()

        for m in SYSTEM_CATALOG:
            m_slug = str(m["slug"])
            catalog_modules.add(m_slug)

            if m_slug not in valid_modules:
                errors.append(
                    f"[catalog→permissions] Módulo '{m_slug}' não está em ModuleSlug."
                )

            for i in m.get("items", []):
                i_slug = str(i["slug"])
                catalog_items.add((m_slug, i_slug))

                if i_slug not in valid_items:
                    errors.append(
                        f"[catalog→permissions] Item '{i_slug}' não está em ItemSlug."
                    )

                for action in i.get("actions", []):
                    codename = f"{m_slug}.{action}_{i_slug}"
                    catalog_perms.add(codename)

        # ══════ 2. Banco x Catálogo ══════
        db_modules = set(Module.objects.values_list("slug", flat=True))
        db_items = set(ModuleItem.objects.values_list(
            "module__slug", "slug"
        ))
        db_perms = set(Permission.objects.values_list("codename", flat=True))

        # módulos no catálogo mas não no banco → precisa sync
        missing_modules = catalog_modules - db_modules
        for s in missing_modules:
            warnings.append(f"[banco] Módulo '{s}' no catálogo mas ausente no banco. Rode sync_catalog.")

        # módulos no banco mas não no catálogo → órfão
        orphan_modules = db_modules - catalog_modules
        for s in orphan_modules:
            warnings.append(f"[banco] Módulo '{s}' no banco mas ausente no catálogo (órfão).")

        # itens
        missing_items = catalog_items - db_items
        for m, i in missing_items:
            warnings.append(f"[banco] Item '{m}.{i}' no catálogo mas ausente no banco.")

        orphan_items = db_items - catalog_items
        for m, i in orphan_items:
            warnings.append(f"[banco] Item '{m}.{i}' no banco mas ausente no catálogo.")

        # permissions
        missing_perms = catalog_perms - db_perms
        for p in missing_perms:
            warnings.append(f"[banco] Permission '{p}' no catálogo mas ausente no banco.")

        orphan_perms = db_perms - catalog_perms
        for p in orphan_perms:
            warnings.append(f"[banco] Permission '{p}' no banco mas ausente no catálogo.")

        # ══════ Relatório ══════
        self.stdout.write(self.style.MIGRATE_HEADING("Validação do catálogo\n"))

        self.stdout.write(
            f"  Catálogo: {len(catalog_modules)} módulos, "
            f"{len(catalog_items)} itens, {len(catalog_perms)} permissions"
        )
        self.stdout.write(
            f"  Banco:    {len(db_modules)} módulos, "
            f"{len(db_items)} itens, {len(db_perms)} permissions\n"
        )

        if errors:
            self.stdout.write(self.style.ERROR(f"\n✗ {len(errors)} erro(s):"))
            for e in errors:
                self.stdout.write(self.style.ERROR(f"  • {e}"))

        if warnings:
            self.stdout.write(self.style.WARNING(f"\n⚠ {len(warnings)} aviso(s):"))
            for w in warnings:
                self.stdout.write(self.style.WARNING(f"  • {w}"))

        if not errors and not warnings:
            self.stdout.write(self.style.SUCCESS("\n✓ Tudo coerente!"))
            sys.exit(0)

        if errors:
            sys.exit(1)

        sys.exit(0)
