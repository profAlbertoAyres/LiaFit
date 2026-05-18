# core/menu/context_processors.py
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _

from core.menu.registry_menu import menu_registry


_SPACE_DASHBOARD_URL_NAME = {
    "personal": "personal:dashboard",
    "tenant": "tenant:dashboard",
    "saas_admin": "saas_admin:dashboard",
}


def menu_context(request):
    if not request.user.is_authenticated:
        return {
            "sidebar_menu": [],
            "dashboard_link": None,
            "profile_link": None,
        }

    return {
        "sidebar_menu": menu_registry.get_menu(request),
        "dashboard_link": _resolve_dashboard_link(request),
        "profile_link": _resolve_profile_link(request),
    }


def _resolve_dashboard_link(request):

    space = getattr(request, "current_space", None)
    url_name = _SPACE_DASHBOARD_URL_NAME.get(space)

    if not url_name:
        return {
            "label": _("Início"),
            "url": reverse("dashboard"),
            "icon": "house",
        }

    kwargs = {}
    if space == "tenant":
        ctx = getattr(request, "context", None)
        org = getattr(ctx, "organization", None) if ctx else None
        if not org:
            return {
                "label": _("Início"),
                "url": reverse("dashboard"),
                "icon": "house",
            }
        kwargs = {"org_slug": org.slug}

    try:
        url = reverse(url_name, kwargs=kwargs)
    except NoReverseMatch:
        url = reverse("dashboard")

    return {
        "label": _("Início"),
        "url": url,
        "icon": "house",
    }

def _resolve_profile_link(request):
    """
    Link universal para o perfil do usuário.
    Disponível em qualquer espaço (personal, tenant, saas_admin).
    """
    try:
        url = reverse("personal:profile")
    except NoReverseMatch:
        return None

    return {
        "label": _("Meu Perfil"),
        "url": url,
        "icon": "user-circle",
    }