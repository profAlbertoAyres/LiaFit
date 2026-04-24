# core/permissions.py
"""
Fonte única da verdade para slugs, itens e permissions do sistema.

Regra de ouro: TODOs slug de módulo/item usado no sistema DEVE estar
declarado aqui. Nunca digite strings soltas em views, catalog ou templates.
"""
from django.db import models


# ════════════════════════════════════════════════════════════
# ENUMS (TextChoices) — usados como `choices=` nos models
# ════════════════════════════════════════════════════════════

class ModuleSlug(models.TextChoices):
    """Todos os módulos do sistema."""
    ACCOUNT    = "account",    "Contas"
    SETTINGS   = "settings",   "Cadastros"
    MY_AREA    = "my-area",    "Minha Área"
    SAAS_ADMIN = "saas-admin", "Admin SaaS"


class ItemSlug(models.TextChoices):
    """Todos os items (cross-module)."""
    # account
    ROLE          = "role",          "Papel"
    MEMBER        = "member",        "Membro"
    ORGANIZATION  = "organization",  "Organização"
    # settings
    CLIENT        = "client",        "Cliente"
    COLLABORATOR  = "collaborator",  "Colaborador"
    # my-area
    DASHBOARD     = "dashboard",     "Dashboard"
    PROFILE       = "profile",       "Perfil"
    # saas-admin
    ORGANIZATIONS = "organizations", "Organizações (Admin)"


class ActionSlug(models.TextChoices):
    VIEW   = "view",   "Visualizar"
    ADD    = "add",    "Adicionar"
    CHANGE = "change", "Alterar"
    DELETE = "delete", "Excluir"


# ════════════════════════════════════════════════════════════
# HELPER para gerar codenames de permissions
# ════════════════════════════════════════════════════════════

class PermSet:
    """
    Gera codenames de permission (ex: 'account.view_role') a partir
    de module+item+actions. Usado nas views.
    """
    def __init__(self, module: str, item: str,
                 actions=(ActionSlug.VIEW, ActionSlug.ADD,
                          ActionSlug.CHANGE, ActionSlug.DELETE)):
        self.module = str(module)
        self.item = str(item)
        self.actions = [str(a) for a in actions]
        for action in self.actions:
            codename = f"{self.module}.{action}_{self.item}"
            setattr(self, action.upper(), codename)

    def all_codenames(self) -> list[str]:
        return [getattr(self, a.upper()) for a in self.actions]


# ════════════════════════════════════════════════════════════
# MÓDULOS — usados nas views (permission_required = ...)
# ════════════════════════════════════════════════════════════

class AccountModule:
    SLUG = ModuleSlug.ACCOUNT
    Client       = PermSet(SLUG, ItemSlug.CLIENT)
    Collaborator = PermSet(SLUG, ItemSlug.COLLABORATOR)


class SettingsModule:
    SLUG = ModuleSlug.SETTINGS
    Role         = PermSet(SLUG, ItemSlug.ROLE)
    Member       = PermSet(SLUG, ItemSlug.MEMBER)
    Organization = PermSet(SLUG, ItemSlug.ORGANIZATION,
                           actions=(ActionSlug.VIEW, ActionSlug.CHANGE))


class MyAreaModule:
    SLUG = ModuleSlug.MY_AREA
    Dashboard = PermSet(SLUG, ItemSlug.DASHBOARD, actions=(ActionSlug.VIEW,))
    Profile   = PermSet(SLUG, ItemSlug.PROFILE,
                        actions=(ActionSlug.VIEW, ActionSlug.CHANGE))


class SaasAdminModule:
    SLUG = ModuleSlug.SAAS_ADMIN
    Organizations = PermSet(SLUG, ItemSlug.ORGANIZATIONS)


# ════════════════════════════════════════════════════════════
# Registry — facilita iteração (usado pelo check_catalog)
# ════════════════════════════════════════════════════════════

ALL_MODULES = [AccountModule, SettingsModule, MyAreaModule, SaasAdminModule]
