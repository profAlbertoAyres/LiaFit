"""
Helpers centralizados de checagem de permissão de alto nível.

Filosofia:
  - is_superuser → ULTRA RARO (você, Alberto). Bypassa tudo.
  - SaaS Staff   → Equipe interna (devs, suporte). Identificada por
                   UserSystemRole com scope=superuser.
  - Tenant Owner → Dono de UMA organização. Manda na ORG dele.
"""

from core.models import SystemRole, UserSystemRole


def is_saas_staff(user) -> bool:
    """
    Verifica se o usuário pertence ao time interno do SaaS.

    Critérios (qualquer um basta):
      1. user.is_superuser → chave-mestra
      2. UserSystemRole ativo com scope='superuser'

    ⚠️ Use SEMPRE este helper em vez de `user.is_superuser` direto
    quando a intenção for "é alguém da equipe Lia Linda?".
    """
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return UserSystemRole.objects.filter(
        user=user,
        is_active=True,
        system_role__scope=SystemRole.Scope.SUPERUSER,
        system_role__is_active=True,
    ).exists()


def is_tenant_owner(user, organization) -> bool:
    """
    Verifica se o usuário é o proprietário (owner) da organização passada.

    Owner = dono da empresa que CONTRATOU o Lia Linda.
    Manda na ORG dele, mas NÃO manda no sistema.
    """
    if not user.is_authenticated or organization is None:
        return False
    return organization.owner_id == user.id
