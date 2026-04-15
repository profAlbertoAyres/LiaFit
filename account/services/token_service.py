from django.utils import timezone
from datetime import timedelta

from account.models import PasswordSetupToken


class TokenService:

    @staticmethod
    def create_token(user):
        PasswordSetupToken.objects.filter(
            user=user,
            used=False
        ).update(used=True)

        return PasswordSetupToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24)
        )

    @staticmethod
    def get_valid_token(token_str):
        try:
            token_obj = PasswordSetupToken.objects.select_related('user').get(
                token=token_str
            )
        except PasswordSetupToken.DoesNotExist:
            return None

        if token_obj.is_valid():
            return token_obj

        return None

    @staticmethod
    def invalidate_user_tokens(user):
        return PasswordSetupToken.objects.filter(
            user=user,
            used=False
        ).update(used=True)