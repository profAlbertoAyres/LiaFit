from datetime import timedelta

from account.models import OnboardingToken


TOKEN_TTL = {
    OnboardingToken.Purpose.ONBOARDING: timedelta(hours=72),
    OnboardingToken.Purpose.RESET_PASSWORD: timedelta(hours=1),
    OnboardingToken.Purpose.EMAIL_CHANGE: timedelta(hours=24),
    OnboardingToken.Purpose.EMAIL_VERIFICATION: timedelta(hours=48),
    OnboardingToken.Purpose.MEMBER_ACTIVATION: timedelta(days=7),
    OnboardingToken.Purpose.MAGIC_LINK: timedelta(minutes=15),
    OnboardingToken.Purpose.ORG_ACTIVATION: timedelta(hours=48),
}

TOKEN_TTL_DEFAULT = timedelta(hours=1)

def get_token_ttl(purpose: str) -> timedelta:

    return TOKEN_TTL.get(purpose, TOKEN_TTL_DEFAULT)

def calculate_expires_at(purpose: str):
    from django.utils import timezone
    return timezone.now() + get_token_ttl(purpose)