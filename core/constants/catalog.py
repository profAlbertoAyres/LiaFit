
# ============================================================
# ACTIONS PADRÃO
# ============================================================

DEFAULT_ACTIONS = ("view", "add", "change", "delete")


# ============================================================
# MÓDULOS E ITEMS
# ============================================================
# Estrutura:
# {
#     "slug": "...",                 # app_label (ex: 'clients')
#     "name": "...",
#     "scope": "tenant|global|superuser",   # default="tenant" se omitido
#     "description": "...",
#     "order": 10,
#     "is_core": bool,               # ativado auto em toda org nova (só faz sentido p/ tenant)
#     "show_in_menu": bool,
#     "items": [
#         {
#             "slug": "...",         # singular; mapeia model_name (ex: 'client')
#             "name": "...",
#             "icon": "...",
#             "order": 10,
#             "show_in_menu": bool,
#             "actions": [...],      # default = DEFAULT_ACTIONS
#             "owner_slug": "...",   # (opcional) slug do Module controlador (owner)
#         },
#     ],
# }

MODULES = [
    # ============================================================
    # TENANT (dentro da organização)
    # ============================================================
    {
        "slug": "account",
        "name": "Configurações",
        "scope": "tenant",
        "description": "Usuários, organizações e membros.",
        "order": 20,
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {"slug": "member",       "name": "Membros",      "icon": "users",     "order": 10, "show_in_menu": True},
            {"slug": "role",         "name": "Papéis",       "icon": "shield",    "order": 20, "show_in_menu": True},
            {
                "slug": "organization",
                "name": "Organização",
                "icon": "briefcase",
                "order": 30,
                "show_in_menu": True,
                "actions": ("view", "change"),
            },
        ],
    },
    {
        "slug": "settings",
        "name": "Cadastros",
        "scope": "tenant",
        "description": "Cadastro e gestão de pessoas.",
        "order": 30,
        "is_core": True,
        "show_in_menu": True,
        "items": [
            {"slug": "client", "name": "Clientes", "icon": "user-check", "order": 10, "show_in_menu": True},
            {"slug": "collaborator", "name": "Colaboradores", "icon": "shield-user", "order": 20, "show_in_menu": True},
        ],
    },

    # ============================================================
    # GLOBAL (área do cliente logado, fora de organização)
    # ============================================================
    {
        "slug": "my-area",
        "name": "Minha Área",
        "scope": "global",
        "description": "Área pessoal do usuário (fora de organização).",
        "order": 100,
        "is_core": False,         
        "show_in_menu": True,
        "items": [
            {
                "slug": "dashboard",
                "name": "Início",
                "icon": "home",
                "order": 10,
                "show_in_menu": True,
                "actions": ("view",),
            },
            {
                "slug": "profile",
                "name": "Meu Perfil",
                "icon": "user",
                "order": 30,
                "show_in_menu": True,
                "actions": ("view", "change"),
            },
        ],
    },

    # ============================================================
    # SUPERUSER (administração da plataforma SaaS)
    # ============================================================
    {
        "slug": "saas-admin",
        "name": "Admin SaaS",
        "scope": "superuser",
        "description": "Administração da plataforma (staff/superuser).",
        "order": 200,
        "is_core": False,
        "show_in_menu": True,
        "items": [
            {
                "slug": "organizations",
                "name": "Organizações",
                "icon": "briefcase",
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
#   - "<codename>"                     → permissão específica (ex: "clients.view_client")
#
# `scope` indica onde o role é criado:
#   - "tenant"    → criado em cada organização (fluxo atual)
#   - "global"    → criado sem organização; pertence ao usuário
#   - "superuser" → criado sem organização; só staff/superuser
#
# Roles sem `scope` assumem "tenant" por padrão.

ROLES = [
    # ---- TENANT ----
    {
        "slug": "owner",
        "name": "Proprietário",
        "scope": "tenant",
        "description": "Dono da organização. Acesso total à organização.",
        "level": 100,
        "permissions": [
            "module:core",
            "module:account",
            "module:clients",
            "module:workouts",
            "module:exercises",
            "module:assessments",
            "module:schedule",
            "module:financial",
        ],
    },
    {
        "slug": "admin",
        "name": "Administrador",
        "scope": "tenant",
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
            "item:financial.invoice",
        ],
    },
    {
        "slug": "professional",
        "name": "Profissional",
        "scope": "tenant",
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
        "scope": "tenant",
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

    # ---- GLOBAL ----
    {
        "slug": "client",
        "name": "Cliente",
        "scope": "global",
        "description": "Usuário comum da plataforma (sem organização).",
        "level": 10,
        "permissions": [
            "module:my-area",
        ],
    },

    # ---- SUPERUSER ----
    {
        "slug": "platform_admin",
        "name": "Admin da Plataforma",
        "scope": "superuser",
        "description": "Administrador global do SaaS (staff/superuser).",
        "level": 1000,
        "permissions": [
            "module:saas-admin",
        ],
    },
]
