"""
Constantes compartilhadas do sistema de espaços.

Centraliza chaves de sessão e outros valores fixos usados pelos
serviços e views relacionados a espaços (Hub, Select, Switch).
"""
from __future__ import annotations

# Chave usada na sessão Django para guardar o último espaço acessado
# pelo usuário. Lida pelo SpaceHubService para decidir se redireciona
# direto ou mostra o hub de seleção.
SESSION_LAST_SPACE_KEY = 'last_space_key'


SPACE_URL_PREFIX_TO_SCOPE: tuple[tuple[str, str], ...] = (
    ('/personal/', 'personal'),
    ('/org/',      'tenant'),
    ('/painel/',   'saas_admin'),
)


def detect_current_space(path: str) -> str | None:
    """
    Detecta o scope do espaço atual a partir do path da URL.

    Args:
        path: request.path (ex: '/org/acme/clients/').

    Returns:
        Um dos values de Module.Scope ('personal' | 'tenant' |
        'saas_admin'), ou None se o path não pertence a nenhum espaço
        (home pública, auth, hub, admin).
    """
    if not path:
        return None
    for prefix, scope in SPACE_URL_PREFIX_TO_SCOPE:
        if path.startswith(prefix):
            return scope
    return None