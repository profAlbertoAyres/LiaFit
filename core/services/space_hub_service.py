"""
Serviço da tela Hub de Seleção de Espaços (/dashboard/).

Responsabilidade ÚNICA: decidir se um usuário autenticado deve ser
redirecionado automaticamente para seu único espaço, ou se deve ver
a tela de seleção com múltiplos espaços disponíveis.

Não confundir com os dashboards de cada papel (org, pessoal, saas admin),
que terão seus próprios services e métricas específicas.
"""
from __future__ import annotations

from typing import Optional

from django.http import HttpRequest

from core.services.space_service import get_user_spaces


class SpaceHubService:
    """Orquestra o comportamento da tela hub de seleção de espaços."""

    @staticmethod
    def get_redirect_url(request: HttpRequest) -> Optional[str]:
        """
        Decide se o usuário deve ser redirecionado direto pra um espaço,
        pulando a tela de seleção.

        Regras:
        - Se a URL já tem `org_slug` (já está dentro de uma org) → não redireciona
        - Se o usuário não está autenticado → não redireciona (deixa o auth tratar)
        - Se o usuário tem exatamente 1 espaço → redireciona pra ele
        - Caso contrário (0 ou 2+) → renderiza a tela hub

        Returns:
            URL de destino, ou None se deve renderizar a tela hub.
        """

        # Sem usuário autenticado → o middleware/decorator de auth resolve
        if not request.user.is_authenticated:
            return None

        spaces = get_user_spaces(request.user)

        # Atalho: usuário com 1 espaço só vai direto pra ele
        if len(spaces) == 1:
            return spaces[0]['url']

        # 0 ou 2+ → renderiza a tela hub
        return None
