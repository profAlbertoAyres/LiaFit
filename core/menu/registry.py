# core/menu/registry.py

"""
Registro central de menus.

Funciona como um "catálogo" onde cada app registra seus menus.
Depois, o context_processor consulta esse catálogo e injeta
os menus visíveis no template.

Uso:
    from core.menu.registry import menu_registry
    menu_registry.register(meu_grupo)
"""


class MenuRegistry:
    """Singleton que armazena todos os grupos de menu."""

    def __init__(self):
        self._groups = []

    def register(self, group):
        """Registra um grupo de menu."""
        self._groups.append(group)

    def get_menu(self, user):
        """
        Retorna os grupos visíveis para o usuário,
        ordenados pelo campo 'order'.
        """
        visible = []

        for group in self._groups:
            if group.is_visible(user):
                visible.append({
                    "label": group.label,
                    "icon": group.icon,
                    "items": [
                        {
                            "label": item.label,
                            "url": item.get_url(),
                            "icon": item.icon,
                            "permission": item.permission,
                        }
                        for item in group.get_visible_items(user)
                    ],
                })

        return sorted(visible, key=lambda g: g.get("order", 0))

    def clear(self):
        """Limpa todos os registros (útil em testes)."""
        self._groups = []


# Instância global — importa isso nos apps
menu_registry = MenuRegistry()
