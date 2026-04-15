from account.models import UserOrganization
from core.models.role_permission import RolePermission
from management.models import OrganizationModule


class ContextService:

    @staticmethod
    def load_roles(user, organization):
        return set(
            UserOrganization.objects.filter(
                user=user,
                organization=organization,
                is_active=True
            ).select_related("role").values_list("role", flat=True)
        )

    @staticmethod
    def load_modules(organization):
        return set(
            OrganizationModule.objects.filter(
                organization=organization,
                is_active=True
            ).values_list("module", flat=True)
        )

    @staticmethod
    def load_permissions(roles, modules):
        permissions = set()

        role_permissions = RolePermission.objects.filter(
            role__in=roles
        ).select_related("permission")

        for rp in role_permissions:
            perm = rp.permission.code
            module = rp.permission.module

            if module in modules:
                permissions.add(perm)

        return permissions