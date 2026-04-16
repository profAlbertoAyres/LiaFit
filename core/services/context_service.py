from account.models import OrganizationMember
from core.models.role_permission import RolePermission
from core.models.organization_module import OrganizationModule


class ContextService:

    @staticmethod
    def load_roles(user, organization):
        """Retorna set de IDs dos roles do usuário naquela organização."""
        return set(
            OrganizationMember.objects.filter(
                user=user,
                organization=organization,
                is_active=True
            ).values_list('role__codename', flat=True)
        )

    @staticmethod
    def load_modules(organization):
        """Retorna set de codenames dos módulos ativos da organização."""
        return set(
            OrganizationModule.objects.filter(
                organization=organization,
                is_active=True
            ).values_list('module__codename', flat=True)
        )

    @staticmethod
    def load_permissions(roles, modules):
        """Retorna set de códigos de permissão filtrados pelos módulos ativos."""
        permissions = set()

        role_permissions = RolePermission.objects.filter(
            role__codename__in=roles
        ).select_related('permission')

        for rp in role_permissions:
            perm = rp.permission.codename
            module = rp.permission.module.codename if rp.permission.module else None

            if module in modules:
                permissions.add(perm)

        return permissions
