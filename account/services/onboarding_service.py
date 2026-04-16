from django.db import transaction
from django.contrib.auth import login
from django.core.exceptions import ValidationError

from account.services.user_service import UserService
from account.services.organization_service import OrganizationService
from account.services.token_service import TokenService


class OnboardingService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data, organization_data, request=None):
        """
        Fluxo: cria User(inactive) + Organization(inactive) + Token
        Org só ativa quando o ADMIN definir a senha via token.
        """
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")

        # 1. Cria ou recupera o usuário (is_active=False)
        user = UserService.get_or_create_user(email, user_data)

        # 2. Cria a organização (active=False)
        organization_data["owner_email"] = email
        organization = OrganizationService.create_organization(organization_data)

        # 3. Vincula user como ADMIN da org
        OrganizationService.add_member(user, organization, role_codename="ADMIN")

        # 4. Cria perfil do usuário
        UserService.setup_profile(user, user_data)

        # 5. Define o dono da org
        organization.owner = user
        organization.save(update_fields=["owner"])

        # 6. Gera token de ativação
        token = TokenService.create_token(user)

        # 7. Envia e-mail (fora da transaction)
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
        Fluxo: valida token → ativa User → ativa Organization → login automático
        """
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
        # Por enquanto, loga no console para desenvolvimento
        setup_url = f"/setup-password/{token.token}/"
        if request:
            setup_url = request.build_absolute_uri(setup_url)

