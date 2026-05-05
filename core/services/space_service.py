"""
Service responsável por descobrir os "espaços" disponíveis para um usuário.

Conceito:
    Um "espaço" é um modo de uso do sistema. Existem 3 tipos:
      - 🟦 personal → Minha Área (universal, todo user tem)
      - 🟩 org      → Uma organização que o user é membro ativo
      - 🟥 saas     → Painel SaaS Admin (equipe interna Lia Linda)

Este service NÃO toma decisões de redirecionamento — só lista o que o user TEM.
Quem decide pra onde mandar é o `resolve_space_destination` (Etapa 2).
"""
from __future__ import annotations


from django.urls import reverse, NoReverseMatch



from django.urls import reverse

from account.models import OrganizationMember
from core.services.permission_service import is_saas_staff


# ----------------------------------------------------------------------
# Constantes de "kind" — usadas como discriminador nos dicts e na session
# ----------------------------------------------------------------------
KIND_PERSONAL = "personal"
KIND_ORG = "org"
KIND_SAAS = "saas"


def get_user_spaces(user) -> list[dict]:
    """
    Retorna a lista de espaços disponíveis para o usuário.

    A ordem é:
      1. Minha Área (sempre primeiro)
      2. Organizações ativas (ordem alfabética por nome)
      3. Admin SaaS (sempre por último, se aplicável)

    Cada espaço é um dict com:
      - kind: 'personal' | 'org' | 'saas'
      - key:  chave única pra session ('personal', 'org:<slug>', 'saas')
      - name: nome exibido no card
      - icon: nome do ícone Lucide
      - url:  URL home do espaço (já resolvida)

    Args:
        user: instância de account.User (ou AnonymousUser).

    Returns:
        list[dict]: lista de espaços. Vazia se user não autenticado.
    """
    # Defensive: user anônimo nunca tem espaços.
    if not user or not user.is_authenticated:
        return []

    spaces: list[dict] = []

    # 1️⃣ Minha Área — universal, todo user autenticado tem.
    spaces.append(_build_personal_space())

    # 2️⃣ Organizações — memberships ativos em orgs ativas.
    spaces.extend(_build_org_spaces(user))

    # 3️⃣ Admin SaaS — só pra equipe interna.
    if is_saas_staff(user):
        spaces.append(_build_saas_space())

    return spaces


# ----------------------------------------------------------------------
# Builders privados — um por tipo de espaço
# ----------------------------------------------------------------------

def _build_personal_space() -> dict:
    """Constrói o card da Minha Área (espaço pessoal/universal)."""
    return {
        "kind": KIND_PERSONAL,
        "key": KIND_PERSONAL,
        "name": "Minha Área",
        "icon": "home",
        "url": reverse("master:dashboard"),
    }


def _build_org_spaces(user) -> list[dict]:
    """
    Busca as organizações ativas onde o user é membro ativo.

    Filtros aplicados:
      - membership.is_active = True
      - organization.is_active = True

    Ordenação: nome da organização (alfabética, case-insensitive).
    """
    memberships = (
        OrganizationMember.objects
        .filter(
            user=user,
            is_active=True,
            organization__is_active=True,
        )
        .select_related("organization")
        .order_by("organization__company_name")
    )

    return [
        {
            "kind": KIND_ORG,
            "key": f"{KIND_ORG}:{m.organization.slug}",
            "name": m.organization.company_name,
            "icon": "building-2",
            "url": reverse("tenant:dashboard", kwargs={"org_slug": m.organization.slug}),
        }
        for m in memberships
    ]

def _safe_reverse(viewname: str, fallback: str = "#") -> str:
    """Resolve URL ou retorna fallback se a rota não existir.

    Útil para serviços de navegação que não devem quebrar caso
    uma URL esteja temporariamente desabilitada/comentada.
    """
    try:
        return reverse(viewname)
    except NoReverseMatch:
        return fallback



def _build_saas_space() -> dict:
    """Constrói o card do painel SaaS Admin (equipe interna)."""
    return {
        "kind": KIND_SAAS,
        "key": KIND_SAAS,
        "name": "Admin SaaS",
        "icon": "server",
        "url": _safe_reverse("saas_admin:dashboard", fallback="/painel/"),
    }
