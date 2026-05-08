"""
View responsável por selecionar um espaço a partir do Hub.

Fluxo:
    1. Usuário clica num card no SpaceHubView (ex.: "Pessoal").
    2. O card aponta pra esta view com ?key=<space_key>.
    3. Gravamos a chave na sessão (last_space_key).
    4. Redirecionamos pra home do espaço escolhido.

Assim, no próximo login/acesso, o SpaceHubService lê a sessão
e leva o usuário direto pro último espaço usado, sem passar
pelo hub de novo.
"""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View

from core.services.space_constants_service import SESSION_LAST_SPACE_KEY


class SpaceSelectView(LoginRequiredMixin, View):
    """Grava o espaço escolhido na sessão e redireciona pra ele."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        space_key = request.GET.get('key')

        # Sem chave -> volta pro hub pra escolher de novo
        if not space_key:
            return redirect('core:space_hub')

        # Persiste o último espaço acessado pra próximas visitas
        request.session[SESSION_LAST_SPACE_KEY] = space_key

        # Redireciona pra rota inicial do espaço escolhido.
        # Convenção: cada espaço tem uma URL nomeada 'space_<key>_home'.
        # Ex.: key='global' -> 'space_global_home'
        return redirect(f'core:space_{space_key}_home')
