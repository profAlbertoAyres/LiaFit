from django.db import transaction
from django.core.exceptions import ValidationError

from account.services.user_service import UserService
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService
from core.services.notification_service import NotificationService
from account.models import UserOrganization


class OnboardingService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):

        email = user_data.get('email')
        if not email:
            raise ValidationError("E-mail não informado.")

        user = UserService.get_or_create_user(email, user_data)

        organization = OrganizationService.create_organization(organization_data)

        OrganizationService.add_user(
            user,
            organization,
            UserOrganization.RoleChoices.ADMIN
        )

        UserService.setup_profile(user, user_data)

        organization.owner = user
        organization.save()

        token = TokenService.create_token(user)

        transaction.on_commit(
            lambda: NotificationService.send_activation_email(
                user,
                organization.company_name,
                token,
                request
            )
        )

        return organization