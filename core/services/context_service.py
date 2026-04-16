from core.models.role_permission import RolePermission
from core.models.organization_module import OrganizationModule


class ContextService:

    @staticmethod
    def load_roles(membership):
        """Retorna set de codenames dos roles do membership."""
        return set(
            membership.roles.values_list('codename', flat=True)
        )

    @staticmethod
    def load_modules(organization):
        """Retorna set de codenames dos módulos ativos da organização."""
        return set(
            OrganizationModule.objects.filter(
                organization=organization,
                is_active=True,
            ).values_list('module__codename', flat=True)
        )

    @staticmethod
    def load_permissions(roles, modules):
        """Retorna set de permissões filtradas pelos módulos ativos."""
        return set(
            RolePermission.objects.filter(
                role__codename__in=roles,
                permission__module__codename__in=modules,
            ).values_list('permission__codename', flat=True)
        )
