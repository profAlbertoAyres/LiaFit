import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from account.constants import calculate_expires_at
from account.exceptions import (
    TokenAlreadyUsedError,
    TokenExpiredError,
    TokenInvalidError,
    TokenPurposeMismatchError,
)
from account.models import OnboardingToken

logger = logging.getLogger(__name__)


class TokenService:
    """Gerencia o ciclo de vida dos OnboardingTokens."""


    @staticmethod
    @transaction.atomic
    def create_token(user, purpose=OnboardingToken.Purpose.ONBOARDING, organization=None, data=None, created_ip=None,
                     created_ua=None, ):

        invalidated = OnboardingToken.objects.filter(user=user, purpose=purpose, used_at__isnull=True,
                                                     expires_at__gt=timezone.now(), ).update(used_at=timezone.now())

        if invalidated:
            logger.info(
                "Invalidados %d token(s) antigo(s) para user=%s purpose=%s",
                invalidated, user.email, purpose,
            )

        # 2. Cria novo token com TTL específico do purpose
        token = OnboardingToken.objects.create(user=user, organization=organization, purpose=purpose,
                                               expires_at=calculate_expires_at(purpose), data=data or {},
                                               created_ip=created_ip, created_ua=(created_ua or "")[:255] or None, )

        logger.info(
            "Token criado: id=%s user=%s purpose=%s expires_at=%s ip=%s",
            token.id, user.email, purpose, token.expires_at, created_ip,
        )
        return token

    # ──────────────── VALIDAÇÃO ────────────────

    @staticmethod
    def get_valid_token(token_str, expected_purpose=None):
        try:
            token_obj = OnboardingToken.objects.select_related(
                "user", "organization"
            ).get(token=token_str)
        except (OnboardingToken.DoesNotExist, ValueError, ValidationError):
            raise TokenInvalidError()

        if token_obj.is_used:
            raise TokenAlreadyUsedError()

        if token_obj.is_expired:
            raise TokenExpiredError()

        if expected_purpose and token_obj.purpose != expected_purpose:
            raise TokenPurposeMismatchError()

        return token_obj

    # ──────────────── CONSUMO ────────────────

    @staticmethod
    def invalidate_token(token_obj, ip=None, user_agent=None):
        token_obj.used_at = timezone.now()
        token_obj.used_ip = ip
        token_obj.used_ua = (user_agent or "")[:255] or None
        token_obj.save(update_fields=["used_at", "used_ip", "used_ua"])

        logger.info(
            "Token consumido: id=%s user=%s purpose=%s ip=%s",
            token_obj.id, token_obj.user.email, token_obj.purpose, ip,
        )
