"""
View da tela Hub de Seleção de Espaços (/dashboard/).

Esta view é o ponto de entrada do usuário autenticado no sistema.
Ela NÃO é um dashboard com métricas — é apenas um "roteador visual"
que apresenta os espaços disponíveis (organizações, área pessoal,
admin SaaS) e deixa o usuário escolher onde quer trabalhar.

Cada espaço terá seu próprio dashboard real, com métricas e dados
específicos do contexto (org, pessoal, saas).
"""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from core.services.space_hub_service import SpaceHubService
from core.services.space_service import get_user_spaces


class SpaceHubView(LoginRequiredMixin, TemplateView):
    """
    Renderiza a tela hub de seleção de espaços.

    Comportamento:
    - Usuário com 1 espaço → redireciona automaticamente (sem renderizar)
    - Usuário com 2+ espaços → mostra cards de seleção
    - Usuário com 0 espaços → mostra estado vazio (caso raro)
    """

    template_name = 'core/space_hub/space_hub.html'

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Intercepta a requisição pra eventualmente redirecionar."""
        redirect_url = SpaceHubService.get_redirect_url(request)
        if redirect_url:
            return redirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Monta o contexto pra renderização da tela hub."""
        context = super().get_context_data(**kwargs)
        spaces = get_user_spaces(self.request.user)

        context.update({
            'spaces': spaces,
            'has_multiple_spaces': len(spaces) >= 2,
        })
        return context
