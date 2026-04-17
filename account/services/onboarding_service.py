import logging

from django.db import transaction
from django.contrib.auth import login
from django.core.exceptions import ValidationError

from account.services.user_service import UserService
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService

logger = logging.getLogger(__name__)


class OnboardingService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")
        print(email)

        user = UserService.get_or_create_user(email)

        organization_data["owner_email"] = email
        organization = OrganizationService.create_organization(organization_data)

        OrganizationService.add_member(user, organization, role_codename="OWNER")

        organization.owner = user
        organization.save(update_fields=["owner"])

        token = TokenService.create_token(user)

        transaction.on_commit(
            lambda: OnboardingService._send_activation_email(
                user, organization, token, request
            )
        )

        return organization

    @staticmethod
    @transaction.atomic
    def setup_password(token_str, password, request=None):
        token_obj = TokenService.get_valid_token(token_str)

        if not token_obj:
            raise ValidationError("Token inválido ou expirado.")

        user = token_obj.user

        # 1. Ativa o usuário e define a senha
        UserService.activate_user(user, password)

        # 2. Ativa a organização
        membership = user.memberships.select_related("organization").first()
        if not membership:
            raise ValidationError("Usuário não vinculado a nenhuma organização.")

        OrganizationService.activate_organization(membership.organization)

        # 3. Invalida o token
        TokenService.invalidate_token(token_obj)

        # 4. Login automático
        if request:
            login(request, user)

        return user


    @staticmethod
    def _send_activation_email(user, organization, token, request=None):
        """
        Envia o e-mail de ativação.
        TODO: implementar com NotificationService real.
        """
        setup_url = f"/setup-password/{token.token}/"
        if request:
            setup_url = request.build_absolute_uri(setup_url)

        # Log bem visível no terminal (modo desenvolvimento)
        print("\n" + "=" * 70)
        print("📧  E-MAIL DE ATIVAÇÃO (DEV)")
        print("-" * 70)
        print(f"  Para:          {user.email}")
        print(f"  Organização:   {organization.company_name}")
        print(f"  Link de setup: {setup_url}")
        print("=" * 70 + "\n")

        # Também registra via logger (aparece se LOGGING estiver configurado)
        logger.info("Link de ativação para %s: %s", user.email, setup_url)

