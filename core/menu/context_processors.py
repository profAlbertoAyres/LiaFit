# core/menu/context_processors.py

"""
Context processor que injeta o menu em TODOS os templates.

Registrar no settings.py:
    TEMPLATES[0]['OPTIONS']['context_processors'] += [
        'core.menu.context_processors.menu_context',
    ]
"""

from core.menu.registry import menu_registry


def menu_context(request):
    """Injeta 'sidebar_menu' no contexto dos templates."""

    # Usuário não logado não tem sidebar
    if not request.user.is_authenticated:
        return {"sidebar_menu": []}

    return {
        "sidebar_menu": menu_registry.get_menu(request.user),
    }
