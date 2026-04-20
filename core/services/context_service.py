from core.models.role_permission import RolePermission
from core.models.organization_module import OrganizationModule


class ContextService:

    @staticmethod
    def load_roles(membership):
        """Retorna set de codenames dos roles do membership."""
        return set(
            membership.roles.values_list('slug', flat=True)
        )

    @staticmethod
    def load_modules(organization):
        return set(
            OrganizationModule.objects.filter(
                organization=organization,
                is_active=True,
            ).values_list('module__name', flat=True)
        )

    @staticmethod
    def load_permissions(roles, modules):
        return set(
            RolePermission.objects.filter(
                role__slug__in=roles,
                permission__item__module__name__in=modules,
            ).values_list('permission__codename', flat=True)
        )
