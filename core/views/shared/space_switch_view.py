"""
View para 'Trocar Espaço'.

Remove apenas a escolha de espaço da sessão e devolve o user
ao Hub de seleção. Não faz logout, não toca em mais nada.
"""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from core.services.space_constants_service import SESSION_LAST_SPACE_KEY


class SpaceSwitchView(LoginRequiredMixin, View):
    """Limpa o último espaço escolhido e volta pro Hub."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request.session.pop(SESSION_LAST_SPACE_KEY, None)
        return redirect(reverse("dashboard"))
