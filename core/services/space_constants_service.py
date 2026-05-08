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
