import logging
from django.core.exceptions import ValidationError
from django.db import transaction

# Importamos as "peças" do nosso motor (o app account)
from account.services.onboarding_service import OnboardingService
from account.services.organization_service import OrganizationService

logger = logging.getLogger(__name__)


class AdminOrganizationService:

    @staticmethod
    @transaction.atomic
    def register_organization(user_data: dict, organization_data: dict, request=None):
        """
        Orquestra a criação de uma organização via Painel SaaS.
        Decide se vincula a um usuário existente ou se faz o fluxo de novo usuário.
        """
        email = user_data.get("email")
        if not email:
            raise ValidationError("E-mail não informado.")

        # 1. Usamos a peça do account para checar o e-mail
        status = OnboardingService.check_email_exists(email)

        # 2. Se o e-mail JÁ EXISTE
        if status.get("exists"):

            if status.get("is_disabled"):
                raise ValidationError(
                    "Este e-mail pertence a um usuário desativado. Reative-o primeiro no painel de usuários.")

            user = status.get("user")

            # Criamos a empresa vinculada ao usuário
            organization = OrganizationService.create_organization(organization_data, owner=user)

            # Já ativamos a empresa imediatamente, pois o usuário já tem conta
            OrganizationService.activate_organization(organization)

            logger.info("Admin SaaS: Organização registrada para usuário existente: user=%s org=%s", user.email,
                        organization.company_name)

            return {
                "organization": organization,
                "user": user,
                "is_new_user": False,
                "message": "Empresa criada e vinculada a um usuário já existente."
            }

        # 3. Se o e-mail NÃO EXISTE
        else:
            # Acionamos o fluxo completo de registro (que cria tudo e envia o token por e-mail)
            organization = OnboardingService.register_organization(
                user_data=user_data,
                organization_data=organization_data,
                request=request
            )

            return {
                "organization": organization,
                "user": organization.owner,
                "is_new_user": True,
                "message": "Nova empresa criada. O novo usuário receberá um e-mail com o link de acesso."
            }
