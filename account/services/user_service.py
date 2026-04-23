import logging

from django.contrib.auth import get_user_model
from django.db import transaction

logger = logging.getLogger(__name__)

User = get_user_model()


class UserService:
    """
    Service responsável por gerenciar a identidade central (User).

    ⚠️ Escopo:
    - Criação e recuperação de usuários
    - Ativação de conta e definição de senha

    ❌ Fora do escopo (responsabilidade de outros services):
    - Criação de "cascas" (Client, Collaborator)
    - Atribuição de papéis (Owner, Professional, Assistant)
    - Dados de perfil específicos de cada casca
    """

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def normalize_email(email: str) -> str:
        """Normaliza email para evitar duplicatas por case/espaços."""
        if not email:
            return email
        return email.strip().lower()

    # ------------------------------------------------------------------ #
    # Criação / Recuperação
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def get_or_create_user(email: str, fullname: str | None = None) -> User:
        """
        Recupera ou cria um User pelo email.

        Usuários criados aqui começam:
        - `is_active=False` (aguardando ativação via token)
        - Com senha inutilizável (`set_unusable_password`)

        Args:
            email: E-mail do usuário (será normalizado).
            fullname: Nome completo (opcional, usado apenas na criação).

        Returns:
            Instância de User (nova ou existente).
        """
        email = UserService.normalize_email(email)

        defaults = {"is_active": False}
        if fullname:
            defaults["fullname"] = fullname

        user, created = User.objects.get_or_create(
            email=email,
            defaults=defaults,
        )

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            logger.info("User criado: %s (id=%s)", user.email, user.pk)
        else:
            logger.debug("User recuperado: %s (id=%s)", user.email, user.pk)

        return user

    # ------------------------------------------------------------------ #
    # Ativação
    # ------------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def activate_user(user: User, password: str) -> User:
        """
        Ativa a conta do usuário definindo a senha inicial.

        Uso típico: após consumo do token de ativação no onboarding.

        Args:
            user: Instância de User a ser ativada.
            password: Senha em texto plano (já validada pelo form).

        Returns:
            A mesma instância de User, atualizada.
        """
        user.set_password(password)
        user.is_active = True
        user.save(update_fields=["password", "is_active"])

        logger.info("User ativado: %s (id=%s)", user.email, user.pk)
        return user
