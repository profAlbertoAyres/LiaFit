# core/management/commands/sync_catalog.py
"""
Sincroniza o banco com o catálogo declarativo (core/constants/catalog.py).

Uso:
    python manage.py sync_catalog
    python manage.py sync_catalog --dry-run
    python manage.py sync_catalog --prune
    python manage.py sync_catalog --skip-bootstrap
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.constants.catalog import SYSTEM_CATALOG
from core.models import Module, ModuleItem, Permission
from core.services.bootstrap import bootstrap_all_organizations_core


class Command(BaseCommand):
    help = "Sincroniza módulos, itens e permissions a partir do catálogo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Mostra o que faria, sem gravar no banco.",
        )
        parser.add_argument(
            "--prune", action="store_true",
            help="Remove do banco registros que não existem mais no catálogo.",
        )
        parser.add_argument(
            "--skip-bootstrap", action="store_true",
            help="Não propaga módulos core para as organizations existentes.",
        )

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        prune = opts["prune"]
        skip_bootstrap = opts["skip_bootstrap"]

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Sincronizando catálogo {'(DRY-RUN)' if dry else ''}"
        ))

        stats = {"modules": 0, "items": 0, "perms": 0, "pruned": 0}

        try:
            with transaction.atomic():
                seen_modules, seen_items, seen_perms = set(), set(), set()

                for m_data in SYSTEM_CATALOG:
                    m_slug = str(m_data["slug"])
                    seen_modules.add(m_slug)

                    module, created = Module.objects.update_or_create(
                        slug=m_slug,
                        defaults={
                            "name": m_data["name"],
                            "icon": m_data.get("icon", ""),
                            "order": m_data.get("order", 0),
                            "scope": m_data.get("scope", "tenant"),
                            "is_core": m_data.get("is_core", False),
                            "show_in_menu": m_data.get("show_in_menu", True),
                            "description": m_data.get("description", ""),
                        },
                    )
                    stats["modules"] += 1
                    self.stdout.write(f"  {'+' if created else '·'} Módulo: {m_slug}")

                    for i_data in m_data.get("items", []):
                        i_slug = str(i_data["slug"])
                        seen_items.add((m_slug, i_slug))

                        item, i_created = ModuleItem.objects.update_or_create(
                            module=module,
                            slug=i_slug,
                            defaults={
                                "name": i_data["name"],
                                "icon": i_data.get("icon", ""),
                                "order": i_data.get("order", 0),
                                "route": i_data.get("route", ""),
                                "show_in_menu": i_data.get("show_in_menu", True),
                                "description": i_data.get("description", ""),
                            },
                        )
                        stats["items"] += 1
                        self.stdout.write(f"      {'+' if i_created else '·'} Item: {i_slug}")

                        for action in i_data.get("actions", []):
                            action_str = str(action)
                            codename = f"{m_slug}.{action_str}_{i_slug}"
                            seen_perms.add(codename)

                            Permission.objects.update_or_create(
                                codename=codename,
                                defaults={
                                    "item": item,
                                    "action": action_str,
                                    "name": f"{i_data['name']} · {action_str}",
                                },
                            )
                            stats["perms"] += 1

                if prune:
                    to_del_perms = Permission.objects.exclude(codename__in=seen_perms)
                    stats["pruned"] += to_del_perms.count()
                    to_del_perms.delete()

                    for item in ModuleItem.objects.all():
                        if (item.module.slug, item.slug) not in seen_items:
                            stats["pruned"] += 1
                            item.delete()

                    to_del_modules = Module.objects.exclude(slug__in=seen_modules)
                    stats["pruned"] += to_del_modules.count()
                    to_del_modules.delete()

                if dry:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("DRY-RUN: nada foi gravado."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))
            raise

        self.stdout.write(self.style.SUCCESS(
            f"\n✓ Catálogo: {stats['modules']} módulos, "
            f"{stats['items']} itens, {stats['perms']} permissions"
            + (f", {stats['pruned']} removidos" if prune else "")
        ))

        # ─── Bootstrap de módulos core nas organizations ──────────────────
        if dry or skip_bootstrap:
            return

        self.stdout.write(self.style.MIGRATE_HEADING(
            "\nPropagando módulos core para as organizations..."
        ))
        b = bootstrap_all_organizations_core()
        self.stdout.write(self.style.SUCCESS(
            f"✓ Bootstrap: {b['orgs']} orgs processadas, "
            f"{b['modules_activated']} OrganizationModule ativados, "
            f"{b['perms_granted']} RolePermission criadas."
        ))
