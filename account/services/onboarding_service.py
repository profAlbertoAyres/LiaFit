import logging

from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from account.exceptions import NoMembershipError
from account.models import OnboardingToken
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService
from account.services.user_service import UserService

logger = logging.getLogger(__name__)
User = get_user_model()


class OnboardingService:

    # ──────────────── REGISTRO INICIAL ────────────────

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")

        extra_fields = {}
        if user_data.get("fullname"):
            extra_fields["fullname"] = user_data["fullname"]

        user = UserService.get_or_create_user(email, extra_fields=extra_fields)
        organization = OrganizationService.create_organization(organization_data, owner=user)

        ip, ua = OnboardingService._extract_request_meta(request)
        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=OnboardingToken.Purpose.ONBOARDING,
            created_ip=ip,
            created_ua=ua,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_email(
                purpose=OnboardingToken.Purpose.ONBOARDING,
                user=user,
                organization=organization,
                token=token,
                request=request,
            )
        )

        logger.info("Organização registrada: user=%s org=%s", user.email, organization.company_name)
        return organization

    # ──────────────── SETUP DE SENHA (ONBOARDING) ────────────────

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
            OnboardingService._secure_login(request, user)

        logger.info(
            "Onboarding concluído: user=%s org=%s",
            user.email, organization.company_name,
        )
        return user

    @staticmethod
    @transaction.atomic
    def resend_password_reset(email, request=None):
        """
        Envia link de redefinição de senha.
        Falha silenciosamente quando o e-mail não existe (anti-enumeration).
        """
        if not email:
            return

        user = User.objects.filter(email__iexact=email.strip()).first()
        if not user or not user.is_active:
            return

        # Reset pressupõe senha já definida. Se ainda não tem, o fluxo
        # correto é a ativação (resend_activation), não reset.
        if OnboardingService._user_needs_password_setup(user):
            logger.info(
                "Reset ignorado: user=%s ainda não definiu senha (usar ativação)",
                user.email,
            )
            return

        # Organização é opcional — reset é do usuário, não da org.
        membership = user.memberships.select_related("organization").first()
        organization = membership.organization if membership else None

        purpose = OnboardingToken.Purpose.RESET_PASSWORD

        ip, ua = OnboardingService._extract_request_meta(request)
        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=purpose,
            created_ip=ip,
            created_ua=ua,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_email(
                purpose=purpose,
                user=user,
                organization=organization,
                token=token,
                request=request,
            )
        )

        logger.info(
            "Envio de reset de senha: user=%s org=%s",
            user.email,
            organization.company_name if organization else "—",
        )

    @staticmethod
    @transaction.atomic
    def confirm_password_reset(token_str, password, request=None):
        if not password:
            raise ValidationError("Senha não informada.")

        token_obj = TokenService.get_valid_token(
            token_str,
            expected_purpose=OnboardingToken.Purpose.RESET_PASSWORD,
        )

        user = token_obj.user
        user.set_password(password)
        # Reset implica e-mail confirmado (pois recebeu o link no inbox)
        if not user.email_verified_at:
            user.email_verified_at = timezone.now()
            user.save(update_fields=["password", "email_verified_at"])
        else:
            user.save(update_fields=["password"])

        ip, ua = OnboardingService._extract_request_meta(request)
        TokenService.invalidate_token(token_obj, ip=ip, user_agent=ua)

        if request:
            OnboardingService._secure_login(request, user)

        logger.info("Senha redefinida: user=%s", user.email)
        return user

    # ──────────────── REGISTRO DE ORG ADICIONAL ────────────────

    @staticmethod
    def check_email_exists(email):
        if not email:
            return {
                "exists": False,
                "user": None,
                "needs_password": False,
                "is_disabled": False,
            }

        user = User.objects.filter(email__iexact=email.strip()).first()
        if not user:
            return {
                "exists": False,
                "user": None,
                "needs_password": False,
                "is_disabled": False,
            }

        return {
            "exists": True,
            "user": user,
            "needs_password": OnboardingService._user_needs_password_setup(user),
            "is_disabled": not user.is_active,
        }

    @staticmethod
    @transaction.atomic
    def register_organization_for_existing_user(user, organization_data, request=None):
        if not user.is_active:
            raise ValidationError(
                "Esta conta está desativada. Entre em contato com o suporte."
            )

        organization = OrganizationService.create_organization(organization_data, owner=user)

        purpose = (
            OnboardingToken.Purpose.ONBOARDING
            if OnboardingService._user_needs_password_setup(user)
            else OnboardingToken.Purpose.ORG_ACTIVATION
        )

        ip, ua = OnboardingService._extract_request_meta(request)
        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=purpose,
            created_ip=ip,
            created_ua=ua,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_email(
                purpose=purpose,
                user=user,
                organization=organization,
                token=token,
                request=request,
            )
        )

        logger.info(
            "Organização adicional registrada: user=%s org=%s purpose=%s",
            user.email, organization.company_name, purpose,
        )
        return organization

    @staticmethod
    @transaction.atomic
    def activate_organization_by_token(token_str, request=None):
        token_obj = TokenService.get_valid_token(
            token_str,
            expected_purpose=OnboardingToken.Purpose.ORG_ACTIVATION,
        )

        user = token_obj.user
        organization = token_obj.organization

        if not organization:
            raise ValidationError("Token sem organização vinculada.")

        OrganizationService.activate_organization(organization)

        ip, ua = OnboardingService._extract_request_meta(request)
        TokenService.invalidate_token(token_obj, ip=ip, user_agent=ua)

        if request:
            OnboardingService._secure_login(request, user)

        logger.info(
            "Organização adicional ativada: user=%s org=%s",
            user.email, organization.company_name,
        )
        return user, organization

    # ──────────────── CONVITE DE MEMBRO ────────────────

    @staticmethod
    @transaction.atomic
    def send_member_activation(membership, request=None):
        user = membership.user
        organization = membership.organization

        ip, ua = OnboardingService._extract_request_meta(request)
        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=OnboardingToken.Purpose.INVITATION,
            created_ip=ip,
            created_ua=ua,
        )

        transaction.on_commit(
            lambda: OnboardingService._send_email(
                purpose=OnboardingToken.Purpose.INVITATION,
                user=user,
                organization=organization,
                token=token,
                request=request,
            )
        )

        logger.info(
            "Ativação de membro enviada: user=%s org=%s",
            user.email, organization.company_name,
        )
        return token

    @staticmethod
    @transaction.atomic
    def activate_member(token_str, password=None, request=None):
        if not password:
            raise ValidationError("Senha não informada.")

        token_obj = TokenService.get_valid_token(
            token_str,
            expected_purpose=OnboardingToken.Purpose.INVITATION,
        )
        user = token_obj.user

        user.set_password(password)
        user.email_verified_at = timezone.now()
        user.is_active = True
        user.save(update_fields=["password", "email_verified_at", "is_active"])

        ip, ua = OnboardingService._extract_request_meta(request)
        TokenService.invalidate_token(token_obj, ip=ip, user_agent=ua)

        if request:
            OnboardingService._secure_login(request, user)

        logger.info(
            "Convite aceito: user=%s org=%s",
            user.email, token_obj.organization.company_name,
        )
        return user

    # ──────────────── REENVIO DE ATIVAÇÃO ────────────────

    @staticmethod
    @transaction.atomic
    def resend_activation(email, request=None, organization=None):
        """
        Reenvia o e-mail de ativação adequado para o usuário.

        Decide automaticamente o purpose do token com base no estado do usuário:
          • Usuário SEM senha + é owner da org    → ONBOARDING
          • Usuário SEM senha + é membro convidado → INVITATION
          • Usuário COM senha (criando org extra)  → ORG_ACTIVATION

        Comportamento silencioso (anti-enumeration): se o e-mail não existir
        ou o usuário não tiver vínculo, retorna sem erro — apenas loga.

        Args:
            email: e-mail do destinatário
            request: HttpRequest (para montar URL absoluta no e-mail)
            organization: Organization específica para reativar.
                Se None, usa a primeira membership encontrada (compatibilidade).
                ⚠️ Recomendado informar quando o usuário tem múltiplas orgs.
        """
        if not email:
            logger.warning("resend_activation: e-mail vazio")
            return

        user = User.objects.filter(email__iexact=email.strip()).first()
        if not user:
            logger.warning("resend_activation: usuário não encontrado para %s", email)
            return

        # Se a organização foi informada, valida que o usuário pertence a ela.
        # Caso contrário, pega a primeira membership (comportamento legado).
        if organization is not None:
            membership = user.memberships.filter(
                organization=organization
            ).select_related("organization").first()
            if not membership:
                logger.warning(
                    "resend_activation: usuário %s não pertence à org %s",
                    user.email, organization.id,
                )
                return
        else:
            membership = user.memberships.select_related("organization").first()
            if not membership:
                logger.warning(
                    "resend_activation: usuário %s sem nenhuma membership",
                    user.email,
                )
                return
            organization = membership.organization

        # Decide o purpose com base no estado do usuário
        if OnboardingService._user_needs_password_setup(user):
            purpose = (
                OnboardingToken.Purpose.ONBOARDING
                if organization.owner_id == user.id
                else OnboardingToken.Purpose.INVITATION
            )
        else:
            purpose = OnboardingToken.Purpose.ORG_ACTIVATION

        token = TokenService.create_token(
            user=user,
            organization=organization,
            purpose=purpose,
        )
        OnboardingService._send_email(
            purpose=purpose,
            user=user,
            organization=organization,
            token=token,
            request=request,
        )
        logger.info(
            "resend_activation: e-mail %s reenviado para %s (org=%s)",
            purpose, user.email, organization.id,
        )

    # ──────────────── HELPERS ────────────────

    @staticmethod
    def _extract_request_meta(request):
        if not request:
            return None, None

        ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR")
        )
        ua = request.META.get("HTTP_USER_AGENT", "")[:500]
        return ip or None, ua or None

    @staticmethod
    def _build_base_url(request=None):
        if request:
            return request.build_absolute_uri('/').rstrip('/')
        return getattr(settings, "BASE_URL", "http://127.0.0.1:8000")

    @staticmethod
    def _user_needs_password_setup(user) -> bool:
        return user.is_shadow or not user.has_usable_password()

    @staticmethod
    def _send_email(purpose, user, organization, token, request=None):
        base_url = OnboardingService._build_base_url(request)

        email_config = {
            OnboardingToken.Purpose.ONBOARDING: {
                "path": "auth/setup-password",
                "title": "📧  E-MAIL DE ATIVAÇÃO (DEV)",
                "label": "Link de setup",
            },
            OnboardingToken.Purpose.INVITATION: {
                "path": "auth/accept-invite",
                "title": "📩  E-MAIL DE CONVITE (DEV)",
                "label": "Link do convite",
            },
            OnboardingToken.Purpose.ORG_ACTIVATION: {
                "path": "auth/activate-organization",
                "title": "🏢  ATIVAR NOVA EMPRESA (DEV)",
                "label": "Link de ativação",
            },
            OnboardingToken.Purpose.RESET_PASSWORD: {
                "path": "auth/reset-password",
                "title": "🔑  RESET DE SENHA (DEV)",
                "label": "Link de redefinição",
            },
        }

        config = email_config.get(purpose)
        if not config:
            logger.warning("Propósito de e-mail desconhecido: %s", purpose)
            return

        url = f"{base_url}/{config['path']}/{token.token}/"
        org_name = organization.company_name if organization else "—"

        # Log visual no console (DEV) — substituir por send_mail() em produção
        print("\n" + "=" * 70)
        print(config["title"])
        print("-" * 70)
        print(f"  Para:          {user.email}")
        print(f"  Organização:   {org_name}")
        print(f"  {config['label']}: {url}")
        print("=" * 70 + "\n")

        logger.info(
            "E-mail (%s) enviado para %s: %s",
            purpose, user.email, url,
        )

    # account/services/onboarding_service.py (topo da classe)

    @staticmethod
    def _secure_login(request, user):
        if request is None:
            return
        request.session.cycle_key()
        login(request, user)

