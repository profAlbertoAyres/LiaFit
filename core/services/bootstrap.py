# core/services/bootstrap.py
"""
Bootstrap de módulos core e permissions por organização.

Um módulo is_core=True deve:
  • Estar SEMPRE ativo (OrganizationModule.is_active=True) em toda Organization.
  • Ter TODAS suas Permissions vinculadas ao Role de maior `level` de cada
    Organization (tipicamente "Proprietário", level=100).
"""
from django.db import transaction

from core.models import (
    Module,
    OrganizationModule,
    Permission,
    Role,
    RolePermission,
)


def activate_core_modules_for_org(organization) -> int:
    """
    Garante OrganizationModule(is_active=True) para todos Module is_core=True.
    Retorna nº de vínculos criados/ativados.
    """
    created_or_updated = 0
    for module in Module.objects.filter(is_core=True, is_active=True):
        om, created = OrganizationModule.objects.update_or_create(
            organization=organization,
            module=module,
            defaults={"is_active": True},
        )
        if created or not om.is_active:
            created_or_updated += 1
    return created_or_updated


def grant_core_permissions_to_owner_role(organization) -> int:
    """
    Vincula TODAS as Permissions de módulos core ao Role de maior `level`
    da organização (owner). Retorna nº de RolePermission criadas.
    """
    owner_role = (
        Role.objects
        .filter(organization=organization, is_active=True)
        .order_by("-level")
        .first()
    )
    if not owner_role:
        return 0

    core_perms = Permission.objects.filter(
        item__module__is_core=True,
        item__module__is_active=True,
        is_active=True,
    )

    created = 0
    for perm in core_perms:
        _, was_created = RolePermission.objects.get_or_create(
            organization=organization,
            role=owner_role,
            permission=perm,
        )
        if was_created:
            created += 1
    return created


@transaction.atomic
def bootstrap_organization_core(organization) -> dict:
    """
    Executa bootstrap completo de uma org: ativa módulos core + concede perms
    ao role owner. Idempotente.
    """
    return {
        "modules_activated": activate_core_modules_for_org(organization),
        "perms_granted": grant_core_permissions_to_owner_role(organization),
    }


@transaction.atomic
def bootstrap_all_organizations_core() -> dict:
    """Aplica bootstrap em TODAS as organizations existentes."""
    from account.models import Organization

    totals = {"orgs": 0, "modules_activated": 0, "perms_granted": 0}
    for org in Organization.objects.all():
        result = bootstrap_organization_core(org)
        totals["orgs"] += 1
        totals["modules_activated"] += result["modules_activated"]
        totals["perms_granted"] += result["perms_granted"]
    return totals
