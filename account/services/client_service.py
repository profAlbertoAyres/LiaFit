import logging

from django.db import transaction
from django.utils import timezone

from account.models import Client, OrganizationClient
from account.services.onboarding_service import OnboardingService
from account.services.user_service import UserService

logger = logging.getLogger(__name__)


class ClientService:

    USER_FIELDS = ('fullname', 'phone', 'cpf', 'gender', 'birth_date')
    ORG_CLIENT_FIELDS = ('objective', 'notes')

    # ──────────────── CREATE ────────────────

    @staticmethod
    @transaction.atomic
    def create_client(organization, data, request=None, created_by=None):
        user = UserService.get_or_create_user(
            email=data['email'],
            extra_fields={
                **{k: data[k] for k in ClientService.USER_FIELDS if data.get(k)},
                'is_active': True,
            },
        )

        client_profile, _ = Client.objects.get_or_create(user=user)

        if OrganizationClient.objects.filter(
            user=client_profile,
            organization=organization,
        ).exists():
            raise ValueError(
                f"{user.fullname or user.email} já é cliente desta organização."
            )

        org_client = OrganizationClient.objects.create(
            user=client_profile,
            organization=organization,
            created_by=created_by,
            **{k: data[k] for k in ClientService.ORG_CLIENT_FIELDS if data.get(k)},
        )

        # 4. E-mail de ativação (apenas para usuário sem senha definida)
        if not user.has_usable_password():
            OnboardingService.send_client_activation(org_client, request=request)

        logger.info(
            "Cliente criado: user=%s org=%s created_by=%s",
            user.email,
            organization.slug,
            created_by.email if created_by else "—",
        )
        return org_client

    # ──────────────── UPDATE ────────────────

    @staticmethod
    @transaction.atomic
    def update_client(org_client, data):
        user = org_client.user.user

        user_updates = {
            k: data[k] for k in ClientService.USER_FIELDS if k in data
        }
        if user_updates:
            for field, value in user_updates.items():
                setattr(user, field, value)
            user.save(update_fields=list(user_updates.keys()))

        org_updates = {
            k: data[k] for k in ClientService.ORG_CLIENT_FIELDS if k in data
        }
        if org_updates:
            for field, value in org_updates.items():
                setattr(org_client, field, value)
            org_client.save(update_fields=list(org_updates.keys()))

        logger.info(
            "Cliente atualizado: user=%s org=%s",
            user.email, org_client.organization.slug,
        )
        return org_client

    # ──────────────── ARCHIVE (soft delete) ────────────────

    @staticmethod
    @transaction.atomic
    def archive_client(org_client):
        if org_client.archived_at is not None:
            return org_client  # idempotente

        org_client.archived_at = timezone.now()
        org_client.save(update_fields=['archived_at'])

        logger.info(
            "Cliente arquivado: user=%s org=%s",
            org_client.user.user.email, org_client.organization.slug,
        )
        return org_client

    # ──────────────── RESEND ACTIVATION ────────────────

    @staticmethod
    def resend_activation(org_client, request=None):
        user = org_client.user.user
        if user.has_usable_password():
            logger.info(
                "Resend ignorado: cliente %s já ativou a conta",
                user.email,
            )
            return None
        return OnboardingService.send_client_activation(
            org_client, request=request,
        )
