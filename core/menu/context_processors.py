# core/menu/context_processors.py
from core.menu.registry import menu_registry

def menu_context(request):
    if not request.user.is_authenticated:
        return {"sidebar_menu": []}

    return {
        "sidebar_menu": menu_registry.get_menu(request), # <-- Aqui
    }
