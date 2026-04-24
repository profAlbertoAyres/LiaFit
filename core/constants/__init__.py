"""
Re-exporta os símbolos públicos do pacote `core.constants`.

Permite:
    from core.constants import MODULES, ROLES, DEFAULT_ACTIONS, SPECIAL_MENU_ROUTES
"""

from core.constants.catalog import DEFAULT_ACTIONS, MODULES, ROLES
from core.constants.menu_routes import SPECIAL_MENU_ROUTES

__all__ = [
    "DEFAULT_ACTIONS",
    "MODULES",
    "ROLES",
    "SPECIAL_MENU_ROUTES",
]
