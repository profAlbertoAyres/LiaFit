from core.models.role import Role
from account.models import Organization, OrganizationMember


class OrganizationService:

    @staticmethod
    def create_organization(data):
        return Organization.objects.create(
            company_name=data['company_name'],
            slug=data['slug'],
            document=data.get('document', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
        )

    @staticmethod
    def add_member(user, organization, role_codename):
        print(role_codename)
        role = Role.objects.get(codename=role_codename)

        membership, created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=organization,
        )
        membership.roles.add(role)

        return membership

    @staticmethod
    def activate_organization(organization):
        """Ativa a organização."""
        organization.is_active = True
        organization.save(update_fields=['is_active'])
