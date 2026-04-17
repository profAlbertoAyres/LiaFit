from django.utils import timezone
from datetime import timedelta

from account.models import OnboardingToken


class TokenService:

    TOKEN_EXPIRY_HOURS = 24

    @staticmethod
    def create_token(user):
        # Invalida tokens anteriores do mesmo usuário
        OnboardingToken.objects.filter(
            user=user,
        )

        return OnboardingToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=TokenService.TOKEN_EXPIRY_HOURS)
        )

    @staticmethod
    def get_valid_token(token_str):
        try:
            token_obj = OnboardingToken.objects.select_related('user').get(
                token=token_str
            )
        except OnboardingToken.DoesNotExist:
            return None

        if token_obj.is_valid():
            return token_obj

        return None

    @staticmethod
    def invalidate_token(token_obj):
        token_obj.used = True
        token_obj.save(update_fields=["used"])
