"""
Management command: bootstrap_core

Uso:
    python manage.py bootstrap_core
        → Sincroniza o catálogo do sistema (Module, ModuleItem, Permission).

    python manage.py bootstrap_core --all-orgs
        → Sincroniza catálogo + aplica bootstrap em TODAS as organizações.

    python manage.py bootstrap_core --org <id>
        → Sincroniza catálogo + aplica bootstrap em UMA organização específica.

    python manage.py bootstrap_core --skip-catalog --all-orgs
        → Pula a sincronização do catálogo (útil se só quer reaplicar bootstrap).
"""

from django.core.management.base import BaseCommand, CommandError
z
from account.models import Organization
from core.bootstrap import bootstrap_organization, sync_system_catalog


class Command(BaseCommand):
    help = "Sincroniza o catálogo do sistema e aplica bootstrap em organizações."

    def add_arguments(self, parser):
        parser.add_argument(
            "--org",
            type=int,
            default=None,
            help="ID de uma organização específica para aplicar bootstrap.",
        )
        parser.add_argument(
            "--all-orgs",
            action="store_true",
            help="Aplica bootstrap em TODAS as organizações cadastradas.",
        )
        parser.add_argument(
            "--skip-catalog",
            action="store_true",
            help="Pula a sincronização do catálogo do sistema.",
        )

    def handle(self, *args, **options):
        org_id = options["org"]
        all_orgs = options["all_orgs"]
        skip_catalog = options["skip_catalog"]

        # ---------------------------------------------------------
        # 1) Sincroniza o catálogo do sistema
        # ---------------------------------------------------------
        if not skip_catalog:
            self.stdout.write(self.style.MIGRATE_HEADING(
                "→ Sincronizando catálogo do sistema..."
            ))
            stats = sync_system_catalog(verbose=True)
            self._print_stats("Catálogo", stats)
        else:
            self.stdout.write(self.style.WARNING(
                "→ Sincronização do catálogo ignorada (--skip-catalog)."
            ))

        # ---------------------------------------------------------
        # 2) Determina quais orgs receberão bootstrap
        # ---------------------------------------------------------
        orgs = None

        if org_id and all_orgs:
            raise CommandError("Use --org OU --all-orgs, não ambos.")

        if org_id:
            try:
                orgs = [Organization.objects.get(pk=org_id)]
            except Organization.DoesNotExist:
                raise CommandError(f"Organização com id={org_id} não encontrada.")

        elif all_orgs:
            orgs = list(Organization.objects.all())
            if not orgs:
                self.stdout.write(self.style.WARNING(
                    "Nenhuma organização cadastrada."
                ))

        # ---------------------------------------------------------
        # 3) Aplica bootstrap nas orgs selecionadas
        # ---------------------------------------------------------
        if orgs:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING(
                f"→ Aplicando bootstrap em {len(orgs)} organização(ões)..."
            ))
            for org in orgs:
                self.stdout.write(f"\n  • {org} (id={org.pk})")
                stats = bootstrap_organization(org, verbose=True)
                self._print_stats(f"  Org '{org}'", stats, indent=4)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✓ Bootstrap concluído."))

    # -----------------------------------------------------------------
    def _print_stats(self, label: str, stats: dict, indent: int = 2) -> None:
        pad = " " * indent
        self.stdout.write(self.style.SUCCESS(f"{pad}✓ {label}:"))
        for key, value in stats.items():
            self.stdout.write(f"{pad}    {key}: {value}")
