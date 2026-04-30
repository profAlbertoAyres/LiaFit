"""
Pacote de roteamento do app `core`.

Submódulos:
    - master_url: rotas do painel administrativo SaaS (tenant master)
    - tenant_url: rotas dos tenants (personal trainers e seus clientes)

As rotas são incluídas em `config/urls.py` via caminho completo, por exemplo:

    include(('core.urls.master_url', 'master'), namespace='master')
    include(('core.urls.tenant_url', 'tenant'), namespace='tenant')

Este `__init__.py` existe apenas para marcar o diretório como
regular package (em vez de namespace package — PEP 420),
mantendo consistência com `account/urls/__init__.py`.
"""
