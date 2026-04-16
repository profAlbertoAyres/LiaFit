from core.models.role import Role
from account.models import Organization, OrganizationMember


class OrganizationService:

    @staticmethod
    def create_organization(data):
        """Cria uma nova organização."""
        return Organization.objects.create(
            name=data['name'],
            slug=data['slug'],
            document=data.get('document', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
        )

    @staticmethod
    def add_member(user, organization, role_codename):
        """Adiciona um membro à organização com um papel específico."""
        role = Role.objects.get(codename=role_codename)

        membership, created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=organization,
            role=role,
            defaults={'is_active': True}
        )

        return membership

    @staticmethod
    def activate_organization(organization):
        """Ativa a organização."""
        organization.is_active = True
        organization.save(update_fields=['is_active'])
