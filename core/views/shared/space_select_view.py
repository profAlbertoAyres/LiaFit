"""
View de seleção de espaço.

Recebe a escolha do usuário no Hub, valida acesso, persiste na sessão
e redireciona para a home do espaço (ou para `?next=` se válido).

Roteada por 3 URLs distintas, todas apontando pra esta view com `kind`
injetado via kwargs do urlpatterns:
  - space/select/personal/              → kind="personal"
  - space/select/org/<slug:org_slug>/   → kind="org"
  - space/select/saas/                  → kind="saas"
"""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from django.views import View

from core.services.space_constants_service import SESSION_LAST_SPACE_KEY
from core.services.space_service import (
    KIND_ORG,
    KIND_PERSONAL,
    KIND_SAAS,
    get_user_spaces,
)


class SpaceSelectView(LoginRequiredMixin, View):
    """
    Persiste a escolha de espaço e redireciona.

    O `kind` vem do urlpatterns (não do usuário) — seguro por design.
    O `org_slug` só existe quando kind == 'org'.
    """

    def get(
        self,
        request: HttpRequest,
        kind: str,
        org_slug: str | None = None,
        *args,
        **kwargs,
    ) -> HttpResponse:
        # Monta a `key` no mesmo formato que get_user_spaces gera.
        # Assim conseguimos achar o espaço na lista do usuário.
        space_key = self._build_space_key(kind, org_slug)

        # Busca espaços do user (single source of truth).
        spaces = get_user_spaces(request.user)
        match = next((s for s in spaces if s["key"] == space_key), None)

        # User não tem acesso a esse espaço → 403.
        if match is None:
            raise PermissionDenied(_("Você não tem acesso a este espaço."))

        request.session[SESSION_LAST_SPACE_KEY] = space_key

        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)

        return redirect(match["url"])

    @staticmethod
    def _build_space_key(kind: str, org_slug: str | None) -> str:
        if kind == KIND_ORG:
            return f"{KIND_ORG}:{org_slug}"
        if kind in (KIND_PERSONAL, KIND_SAAS):
            return kind
        raise PermissionDenied(_("Tipo de espaço inválido."))
