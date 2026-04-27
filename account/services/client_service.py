from datetime import date

from django.db import transaction

from account.models import Client, ClientProfessional
from account.services.organization_service import OrganizationService
from account.services.user_service import UserService


class ClientService:

    USER_FIELDS = ('fullname', 'phone', 'gender', 'cpf', 'birth_date')

    @staticmethod
    @transaction.atomic
    def create_client(organization, professional, user_data, client_data):
        user = UserService.get_or_create_user(
            email=user_data['email'],
            extra_fields={k: user_data[k] for k in ClientService.USER_FIELDS if user_data.get(k)},
        )

        OrganizationService.add_member(
            user=user,
            organization=organization,
            role_codenames='client',
        )

        client = Client.objects.create(
            user=user,
            organization=organization,
            **client_data,
        )

        ClientProfessional.objects.create(
            client=client,
            professional=professional,
            start_date=date.today(),
            is_active=True,
        )

        return client
