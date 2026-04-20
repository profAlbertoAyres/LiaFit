"""
Catálogo declarativo do sistema LiaFit.

Fonte única de verdade para:
- Módulos do sistema
- Items (telas/rotas/models) de cada módulo
- Actions (permissões) por item
- Roles padrão e suas permissões

Alterações aqui são aplicadas via `python manage.py bootstrap_core`.
"""

# ============================================================
# ACTIONS PADRÃO
# ============================================================
# Cada item de módulo gera automaticamente as 4 permissões nativas do Django,
# salvo quando `actions` é explicitado no item.

DEFAULT_ACTIONS = ("view", "add", "change", "delete")


# ============================================================
# MÓDULOS E ITEMS
# ============================================================
# Estrutura:
# {
#     "slug": "...",             # Mapeia para o app_label no Django (ex: 'clients')
#     "name": "...",
#     "description": "...",
#     "order": 10,
#     "is_core": bool,           # módulos core são ativados automaticamente em toda org
#     "show_in_menu": bool,
#     "items": [
#         {
#             "slug": "...",              # NO SINGULAR! Mapeia para o model_name no Django (ex: 'client')
#             "name": "...",
#             "url_name": "...",          # opcional (name da URL Django)
#             "icon": "...",              # opcional
#             "order": 10,
#             "show_in_menu": bool,
#             "actions": [...],           # opcional; default = DEFAULT_ACTIONS
#         },
#     ],
# }

MODULES = [
    {
        "slug": "core",
        "name": "Core",
        "description": "Base do sistema (dashboard, configurações gerais).",
        "order": 10,
        "is_core": True,
        "show_in_menu": False,
        "items": [
            {
                "slug": "dashboard",
                "name": "Dashboard",
                "url_name": "core:dashboard",
                "icon": "home",
                "order": 10,
                "show_in_menu": True,
                "actions": ("view",),
            },
        ],
    },
    {
        "slug": "account",
        "name": "Contas",
        "description": "Usuários, organizações e membros.",
        "order": 20,
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": "member",
                "name": "Membros",
                "url_name": "account:member_list",
                "icon": "users",
                "order": 10,
                "show_in_menu": True,
            },
            {
                "slug": "role",
                "name": "Papéis",
                "url_name": "account:role_list",
                "icon": "shield",
                "order": 20,
                "show_in_menu": True,
            },
            {
                "slug": "organization",
                "name": "Organização",
                "url_name": "account:organization_detail",
                "icon": "briefcase",
                "order": 30,
                "show_in_menu": True,
                "actions": ("view", "change"),
            },
        ],
    },
    {
        "slug": "clients",
        "name": "Clientes",
        "description": "Cadastro e gestão de alunos.",
        "order": 30,
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {
                "slug": "client",
                "name": "Clientes",
                "url_name": "clients:client_list",
                "icon": "user-check",
                "order": 10,
                "show_in_menu": True,
            },
        ],
    },
    {
        "slug": "workouts",
        "name": "Treinos",
        "description": "Montagem e prescrição de treinos.",
        "order": 40,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "workout",
                "name": "Treinos",
                "url_name": "workouts:workout_list",
                "icon": "activity",
                "order": 10,
                "show_in_menu": True,
            },
            {
                "slug": "template",
                "name": "Modelos",
                "url_name": "workouts:template_list",
                "icon": "layout",
                "order": 20,
                "show_in_menu": True,
            },
        ],
    },
    {
        "slug": "exercises",
        "name": "Exercícios",
        "description": "Biblioteca de exercícios.",
        "order": 50,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "exercise",
                "name": "Exercícios",
                "url_name": "exercises:exercise_list",
                "icon": "dumbbell",
                "order": 10,
                "show_in_menu": True,
            },
        ],
    },
    {
        "slug": "assessments",
        "name": "Avaliações",
        "description": "Avaliações físicas dos alunos.",
        "order": 60,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "assessment",
                "name": "Avaliações",
                "url_name": "assessments:assessment_list",
                "icon": "clipboard",
                "order": 10,
                "show_in_menu": True,
            },
        ],
    },
    {
        "slug": "schedule",
        "name": "Agenda",
        "description": "Agendamentos e compromissos.",
        "order": 70,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "appointment",
                "name": "Agendamentos",
                "url_name": "schedule:appointment_list",
                "icon": "calendar",
                "order": 10,
                "show_in_menu": True,
            },
        ],
    },
    {
        "slug": "financial",
        "name": "Financeiro",
        "description": "Mensalidades e pagamentos.",
        "order": 80,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "invoice",
                "name": "Mensalidades",
                "url_name": "financial:invoice_list",
                "icon": "dollar-sign",
                "order": 10,
                "show_in_menu": True,
            },
            {
                "slug": "payment",
                "name": "Pagamentos",
                "url_name": "financial:payment_list",
                "icon": "credit-card",
                "order": 20,
                "show_in_menu": True,
            },
        ],
    },
]


# ============================================================
# ROLES PADRÃO
# ============================================================
# `permissions` aceita:
#   - "*"                              → todas as permissões do sistema
#   - "module:<module_slug>"           → todas as permissões do módulo
#   - "item:<module_slug>.<item_slug>" → todas as permissões do item
#   - "<codename>"                     → permissão específica
#
# O codename agora segue o padrão oficial do Django: "<app_label>.<action>_<model_name>"
# Ex.: "clients.view_client"

ROLES = [
    {
        "slug": "owner",
        "name": "Proprietário",
        "description": "Dono da organização. Acesso total ao sistema.",
        "level": 100,
        "permissions": ["*"],
    },
    {
        "slug": "admin",
        "name": "Administrador",
        "description": "Gerencia toda a organização exceto billing.",
        "level": 80,
        "permissions": [
            "module:core",
            "module:account",
            "module:clients",
            "module:workouts",
            "module:exercises",
            "module:assessments",
            "module:schedule",
            "item:financial.invoice",  # Atualizado para o slug no singular
        ],
    },
    {
        "slug": "professional",
        "name": "Profissional",
        "description": "Personal/professor. Acessa alunos, treinos e avaliações.",
        "level": 50,
        "permissions": [
            "core.view_dashboard",
            "module:clients",
            "module:workouts",
            "module:exercises",
            "module:assessments",
            "schedule.view_appointment",
            "schedule.add_appointment",
            "schedule.change_appointment",
        ],
    },
    {
        "slug": "assistant",
        "name": "Assistente",
        "description": "Recepção/secretaria. Agenda e cadastros básicos.",
        "level": 30,
        "permissions": [
            "core.view_dashboard",
            "clients.view_client",
            "clients.add_client",
            "clients.change_client",
            "module:schedule",
            "financial.view_invoice",
        ],
    },
]
