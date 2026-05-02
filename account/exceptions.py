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



# ──────────────── Role Assignment ────────────────
class RoleAssignmentError(AccountError):
    default_message = "Erro na atribuição de papel."


class RoleAssignmentHierarchyError(RoleAssignmentError):
    default_message = "Você não pode mexer em papéis com nível igual ou superior ao seu."


class RoleAssignmentLastRoleError(RoleAssignmentError):
    default_message = "Não é possível remover o último papel de um membro."


class RoleAssignmentSelfError(RoleAssignmentError):
    default_message = "Você não pode alterar seus próprios papéis."


class RoleAssignmentOwnerError(RoleAssignmentError):
    default_message = "Os papéis do proprietário da organização são protegidos."


class RoleAssignmentDuplicateError(RoleAssignmentError):
    default_message = "Este membro já possui esse papel."


class RoleAssignmentNotFoundError(RoleAssignmentError):
    default_message = "Atribuição de papel não encontrada."


class UndoWindowExpiredError(RoleAssignmentError):
    default_message = "A janela de desfazer expirou."


class UndoAlreadyDoneError(RoleAssignmentError):
    default_message = "Esta ação já foi desfeita."
