import logging

from django.conf import settings  # ← corrigido
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.db import transaction

from account.exceptions import NoMembershipError
from account.models import OnboardingToken
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService
from account.services.user_service import UserService

logger = logging.getLogger(__name__)


class OnboardingService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")

        user = UserService.get_or_create_user(email)

        organization_data["owner_email"] = email
        organization = OrganizationService.create_organization(organization_data)
        OrganizationService.add_member(user, organization, role_codename="OWNER")

        organization.owner = user
        organization.save(update_fields=["owner"])

        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=OnboardingToken.Purpose.ONBOARDING,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_activation_email(
                user, organization, token, request
            )
        )

        return organization

    @staticmethod
    @transaction.atomic
    def setup_password(token_str, password, request=None):
        """
        Consome um token de ONBOARDING para ativar user + organização.

        Raises:
            TokenInvalidError, TokenExpiredError, TokenAlreadyUsedError,
            TokenPurposeMismatchError, NoMembershipError, ValidationError
        """
        # 1. Valida token (já lança exceptions específicas)
        token_obj = TokenService.get_valid_token(
            token_str,
            expected_purpose=OnboardingToken.Purpose.ONBOARDING,
        )

        user = token_obj.user

        # 2. Ativa usuário (define senha, marca email_verified_at, is_active)
        UserService.activate_user(user, password)

        # 3. Busca organização via token (mais confiável que memberships.first())
        organization = token_obj.organization
        if not organization:
            # Fallback: se token não tem org, tenta via membership
            membership = user.memberships.select_related("organization").first()
            if not membership:
                raise NoMembershipError()
            organization = membership.organization

        # 4. Ativa organização
        OrganizationService.activate_organization(organization)

        # 5. Invalida token (com rastreio de IP/UA)
        ip, ua = OnboardingService._extract_request_meta(request)
        TokenService.invalidate_token(token_obj, ip=ip, user_agent=ua)

        # 6. Auto-login opcional
        if request:
            login(request, user)

        logger.info(
            "Onboarding concluído: user=%s org=%s",
            user.email, organization.company_name
        )

        return user

    # ──────────────── Helpers privados ────────────────

    @staticmethod
    def _extract_request_meta(request):
        """Extrai IP e User-Agent do request (None-safe)."""
        if not request:
            return None, None

        # IP (respeita proxy reverso)
        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR")
        )
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]  # trunca por segurança
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
