from django.db import transaction

from account.models import Assistant, AssistantProfessional, UserOrganization
from account.services.user_service import UserService


class AssistantService:

    @staticmethod
    @transaction.atomic
    def create_assistant(organization, professional_owner, user_data):

        user = UserService.get_or_create_user(
            email=user_data['email'],
            user_data=user_data
        )

        UserOrganization.objects.get_or_create(
            user=user,
            organization=organization,
            role='assistant'
        )

        UserService.setup_profile(user, user_data)

        assistant = Assistant.objects.create(
            user=user,
            organization=organization
        )

        AssistantProfessional.objects.create(
            assistant=assistant,
            professional=professional_owner,
            is_active=True
        )

        return assistant