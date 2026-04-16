from django.db import transaction

from account.models import Professional
from account.services.user_service import UserService
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService


class ProfessionalService:

    @staticmethod
    @transaction.atomic
    def create_professional(organization, user_data, cref, specialization=None, biography=None):

        user = UserService.get_or_create_user(
            email=user_data["email"],
            user_data=user_data
        )

        OrganizationService.add_member(user, organization, role_codename="PROFESSIONAL")

        UserService.setup_profile(user, user_data)

        professional = Professional.objects.create(
            user=user,
            organization=organization,
            cref=cref,
            specialization=specialization,
            biography=biography,
        )

        # Gera token para o profissional definir senha
        token = TokenService.create_token(user)

        return professional, token
