from django.db import transaction

from core.constants import ROLES
from core.models import Role, RolePermission, Module, OrganizationModule, Permission
from core.services.bootstrap.catalog_service import resolve_permissions

OWNER_ROLE_SLUG = "owner"

@transaction.atomic
def bootstrap_organization(organization, *, verbose: bool = False) -> dict:
    stats = {
        "modules_enabled": 0,
        "roles_created": 0,
        "roles_updated": 0,
        "role_permissions_created": 0,
        "universal_permissions_granted": 0,
        "owner_role_assigned": False,
    }

    # --- 1) Ativar módulos core do tenant ---
    # 🛡️ Filtro DUPLO: is_core=True E scope=TENANT
    # Nunca deve ativar módulos de scope=SUPERUSER em tenants!
    core_modules = Module.objects.filter(
        is_core=True,
        scope=Module.Scope.TENANT,
    ).exclude(scope=Module.Scope.SAAS_ADMIN)  # 🛡️ defesa extra

    for module in core_modules:
        # 🛡️ Sanity check: nunca deveria passar daqui se não for tenant
        if module.scope != Module.Scope.TENANT:
            if verbose:
                print(f"  [⚠️] PULANDO módulo {module.slug} (scope={module.scope})")
            continue

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
        if role_def.get("scope", Module.Scope.TENANT) != Module.Scope.TENANT:
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

        permissions = resolve_permissions(
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

    # --- 3) 🌐 Permissões UNIVERSAIS a TODOS os roles ---
    universal_perms = Permission.objects.filter(
        item__module__is_universal=True,
        item__module__scope=Module.Scope.TENANT,
        is_active=True,
    )
    all_roles = Role.objects.filter(organization=organization)

    for role in all_roles:
        for perm in universal_perms:
            _, created = RolePermission.objects.get_or_create(
                organization=organization,
                role=role,
                permission=perm,
            )
            if created:
                stats["universal_permissions_granted"] += 1
                if verbose:
                    print(f"  [🌐] {role.slug} ← {perm.codename}")

    # --- 4) Garantir owner ---
    if organization.owner_id:
        from account.models import OrganizationMember

        owner_role = Role.objects.get(organization=organization, slug=OWNER_ROLE_SLUG)
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


# ============================================================
# 4) PROPAGAÇÃO DE MÓDULOS CORE (para orgs já existentes)
# ============================================================

@transaction.atomic
def propagate_core_modules_to_all_orgs(*, verbose: bool = False) -> dict:
    """
    Propaga módulos core E permissões universais para TODAS as orgs.

    🛡️ AUTO-LIMPEZA: remove OrganizationModule de scope=superuser
    que possam ter sido criados por engano em versões antigas.

    Idempotente.
    """
    from account.models import Organization

    stats = {
        "organizations_processed": 0,
        "modules_activated": 0,
        "modules_cleaned": 0,  # 🆕
        "owner_permissions_granted": 0,
        "universal_permissions_granted": 0,
    }


    invalid_oms = OrganizationModule.objects.filter(
        module__scope=Module.Scope.SAAS_ADMIN,
    )
    invalid_count = invalid_oms.count()
    if invalid_count > 0:
        if verbose:
            print(f"  [🧹] Limpando {invalid_count} módulo(s) superuser ativados em tenants...")
            for om in invalid_oms:
                print(f"      ❌ {om.organization} → {om.module.slug}")
        invalid_oms.delete()
        stats["modules_cleaned"] = invalid_count

    # 🛡️ Filtros explícitos com scope=TENANT
    core_modules = Module.objects.filter(
        is_core=True,
        scope=Module.Scope.TENANT,
    )
    core_perms = Permission.objects.filter(
        item__module__is_core=True,
        item__module__scope=Module.Scope.TENANT,
        is_active=True,
    )
    universal_perms = Permission.objects.filter(
        item__module__is_universal=True,
        item__module__scope=Module.Scope.TENANT,
        is_active=True,
    )

    for org in Organization.objects.all():
        stats["organizations_processed"] += 1

        # 1) Ativar módulos core
        for module in core_modules:
            # 🛡️ Sanity check (defesa em profundidade)
            if module.scope != Module.Scope.TENANT:
                continue

            _, created = OrganizationModule.objects.get_or_create(
                organization=org,
                module=module,
                defaults={"is_active": True},
            )
            if created:
                stats["modules_activated"] += 1
                if verbose:
                    print(f"  [+] {org} → módulo {module.slug} ativado")

        # 2) Owner role com permissions core
        owner_role = Role.objects.filter(organization=org, slug=OWNER_ROLE_SLUG).first()

        if not owner_role:
            if verbose:
                print(f"  [!] {org} sem role 'owner' — pule bootstrap_organization antes")
            continue

        for perm in core_perms:
            _, created = RolePermission.objects.get_or_create(
                organization=org,
                role=owner_role,
                permission=perm,
            )
            if created:
                stats["owner_permissions_granted"] += 1

        # 3) 🌐 Universais a TODOS os roles
        all_roles = Role.objects.filter(organization=org)
        for role in all_roles:
            for perm in universal_perms:
                _, created = RolePermission.objects.get_or_create(
                    organization=org,
                    role=role,
                    permission=perm,
                )
                if created:
                    stats["universal_permissions_granted"] += 1
                    if verbose:
                        print(f"  [🌐] {org} → {role.slug} ← {perm.codename}")

    return stats
