from django.db import transaction
from datetime import date

from account.models import Client, ClientProfessional
from account.services.user_service import UserService
from account.services.organization_service import OrganizationService


class ClientService:

    @staticmethod
    @transaction.atomic
    def create_client(organization, professional, user_data, client_data):

        user = UserService.get_or_create_user(
            email=user_data["email"],
            user_data=user_data
        )

        OrganizationService.add_member(user, organization, role_codename="CLIENT")

        UserService.setup_profile(user, user_data)

        client = Client.objects.create(
            user=user,
            organization=organization,
            **client_data
        )

        ClientProfessional.objects.create(
            client=client,
            professional=professional,
            start_date=date.today(),
            is_active=True,
        )

        return client

