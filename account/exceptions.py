class AccountError(Exception):
    """Base para todas as exceptions do app account."""
    default_message = "Erro na operação de conta."

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


# ──────────────── Token ────────────────
class TokenError(AccountError):
    default_message = "Erro relacionado ao token."


class TokenInvalidError(TokenError):
    default_message = "Token inválido."


class TokenExpiredError(TokenError):
    default_message = "Token expirado. Solicite um novo link."


class TokenAlreadyUsedError(TokenError):
    default_message = "Este token já foi utilizado."


class TokenPurposeMismatchError(TokenError):
    default_message = "Token não é válido para esta operação."


# ──────────────── Onboarding ────────────────
class OnboardingError(AccountError):
    default_message = "Erro no processo de onboarding."


class NoMembershipError(OnboardingError):
    default_message = "Usuário não está vinculado a nenhuma organização."


# ──────────────── User ────────────────
class UserError(AccountError):
    default_message = "Erro na operação do usuário."


class UserAlreadyActiveError(UserError):
    default_message = "Usuário já está ativo."