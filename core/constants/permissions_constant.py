# core/constants/permissions_constant.py
"""
Enums de slugs. Fonte única dos valores válidos.
Usados como choices nos models e como chaves no catálogo.
"""
from django.db import models


class ModuleSlug(models.TextChoices):
    ACCOUNT    = "account",    "Cadastros"
    SETTINGS   = "settings",   "Configurações"
    MY_AREA    = "my-area",    "Minha Área"
    SAAS_ADMIN = "saas-admin", "Admin SaaS"


class ItemSlug(models.TextChoices):
    # account
    CLIENT          = "client",        "Cliente"
    # settings
    ROLE            = "role",          "Papel"
    MEMBER          = "member",        "Membro"
    ORGANIZATION    = "organization",  "Organização"
    # my-area
    DASHBOARD       = "dashboard",     "Dashboard"
    PROFILE         = "profile",       "Perfil"
    # saas-admin
    ORGANIZATIONS   = "organizations", "Organizações (Admin)"
    USERS_ADMIN     = "users-admin", "Usuários (Admin)"
    DASHBOARD_ADMIN = "dashboard-admin", "Painel Admin"
    SPECIALTY       = "specialty", "Especialidades"

class ActionSlug(models.TextChoices):
    VIEW   = "view",   "Visualizar"
    ADD    = "add",    "Adicionar"
    CHANGE = "change", "Alterar"
    DELETE = "delete", "Excluir"
    INVITE = "invite", "Convidar" 

class SystemRoleSlug(models.TextChoices):
    SUPERADMIN = "superadmin", "Super Administrador"
    CLIENT     = "client",     "Cliente" 