from django.db import transaction

from core.models.role import Role
from account.models import Assistant, OrganizationMember


class AssistantService:

    @staticmethod
    @transaction.atomic
    def create_assistant(organization, professional_member, user, data):
        """
        Cria um assistente vinculado a uma organização.
        """
        # 1. Busca o role de assistente
        role = Role.objects.get(codename='assistant')

        # 2. Cria o vínculo com a organização
        membership, _ = OrganizationMember.objects.get_or_create(
            user=user,
            organization=organization,
            role=role,
            defaults={'is_active': True}
        )

        # 3. Cria o perfil de assistente
        assistant = Assistant.objects.create(
            member=membership,
            department=data.get('department', '')
        )

        return assistant
