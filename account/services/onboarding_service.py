import logging

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from account.exceptions import NoMembershipError
from account.models import OnboardingToken
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService
from account.services.user_service import UserService

logger = logging.getLogger(__name__)
User = get_user_model()


class OnboardingService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")

        fullname = user_data.get("fullname")

        # 1. Pega ou cria o usuário base
        user = UserService.get_or_create_user(email, fullname=fullname)


        organization = OrganizationService.create_organization(organization_data, owner=user)

        # 3. Cria o token de onboarding para o usuário criar a senha
        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=OnboardingToken.Purpose.ONBOARDING,
        )

        # 4. Envia o e-mail apenas se tudo deu certo no banco de dados
        transaction.on_commit(
            lambda: OnboardingService._send_activation_email(
                user, organization, token, request
            )
        )

        return organization

    @staticmethod
    @transaction.atomic
    def setup_password(token_str, password, request=None):
        token_obj = TokenService.get_valid_token(
            token_str,
            expected_purpose=OnboardingToken.Purpose.ONBOARDING,
        )

        user = token_obj.user

        UserService.activate_user(user, password)

        organization = token_obj.organization
        if not organization:
            membership = user.memberships.select_related("organization").first()
            if not membership:
                raise NoMembershipError()
            organization = membership.organization

        OrganizationService.activate_organization(organization)

        ip, ua = OnboardingService._extract_request_meta(request)
        TokenService.invalidate_token(token_obj, ip=ip, user_agent=ua)

        if request:
            login(request, user)

        logger.info(
            "Onboarding concluído: user=%s org=%s",
            user.email, organization.company_name
        )

        return user

    @staticmethod
    @transaction.atomic
    def resend_password_token(email, request=None):
        if not email:
            return

        user = (
            User.objects
            .filter(email__iexact=email.strip())
            .first()
        )
        if not user:
            return

        membership = user.memberships.select_related("organization").first()
        if not membership:
            return

        organization = membership.organization
        ip, ua = OnboardingService._extract_request_meta(request)

        token = TokenService.create_token(
            user=user,
            purpose=OnboardingToken.Purpose.ONBOARDING,
            organization=organization,
            created_ip=ip,
            created_ua=ua,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_activation_email(
                user, organization, token, request
            )
        )

        logger.info(
            "Reenvio de ativação solicitado: user=%s org=%s",
            user.email, organization.company_name
        )

    @staticmethod
    def _extract_request_meta(request):
        """Extrai IP e User-Agent do request (None-safe)."""
        if not request:
            return None, None

        ip = (
                request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                or request.META.get("REMOTE_ADDR")
        )
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]
        return ip or None, ua or None

    @staticmethod
    def _send_activation_email(user, organization, token, request=None):
        if request:
            base_url = request.build_absolute_uri('/').rstrip('/')
        else:
            base_url = getattr(settings, "BASE_URL", "http://127.0.0.1:8000")

        setup_url = f"{base_url}/auth/setup-password/{token.token}/"

        print("\n" + "=" * 70)
        print("📧  E-MAIL DE ATIVAÇÃO (DEV)")
        print("-" * 70)
        print(f"  Para:          {user.email}")
        print(f"  Organização:   {organization.company_name}")
        print(f"  Link de setup: {setup_url}")
        print("=" * 70 + "\n")

        logger.info("Link de ativação para %s: %s", user.email, setup_url)
