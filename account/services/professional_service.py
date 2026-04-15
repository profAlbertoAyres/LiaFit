from django.db import transaction

from account.models import Professional, UserOrganization
from account.services.user_service import UserService


class ProfessionalService:

    @staticmethod
    @transaction.atomic
    def create_professional(organization, user_data, cref, specialization=None, biography=None):

        user = UserService.get_or_create_user(
            email=user_data['email'],
            user_data=user_data
        )

        UserOrganization.objects.get_or_create(
            user=user,
            organization=organization,
            role='professional'
        )

        UserService.setup_profile(user, user_data)

        professional = Professional.objects.create(
            user=user,
            organization=organization,
            cref=cref,
            specialization=specialization,
            biography=biography
        )

        return professional