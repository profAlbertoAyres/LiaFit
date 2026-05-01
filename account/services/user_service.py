import logging

from django.contrib.auth import get_user_model
from django.db import transaction

logger = logging.getLogger(__name__)

User = get_user_model()


class UserService:


    @staticmethod
    def normalize_email(email: str) -> str:
        if not email:
            return email
        return email.strip().lower()


    @staticmethod
    @transaction.atomic
    def get_or_create_user(email: str, extra_fields: dict | None = None) -> User:

        email = UserService.normalize_email(email)

        defaults = {"is_active": False, **(extra_fields or {})}

        user, created = User.objects.get_or_create(email=email, defaults=defaults)

        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            logger.info("User criado: %s (id=%s)", user.email, user.pk)
        else:
            logger.debug("User recuperado: %s (id=%s)", user.email, user.pk)

        return user


    @staticmethod
    @transaction.atomic
    def activate_user(user: User, password: str) -> User:

        user.set_password(password)
        user.is_active = True
        user.save(update_fields=["password", "is_active"])

        logger.info("User ativado: %s (id=%s)", user.email, user.pk)
        return user
