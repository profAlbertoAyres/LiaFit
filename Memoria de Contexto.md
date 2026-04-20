# 📋 NotasDev - LiaFit

> Documento de acompanhamento do desenvolvimento do sistema LiaFit.
> Atualizado em: 18/04/2026

---

## 📐 Arquitetura Geral

### Tipo de Sistema
- **SaaS Multi-tenant** com módulos contratáveis
- **Tenant por URL**: `/org/{slug}/...`
- **Django 5.x** + **Tailwind CSS** + **HTMX**
- **Banco**: PostgreSQL

### Estrutura de Apps

.
├── NOTAS_DEV.md
├── agente.md
├── agests.md
├── contexto_auth.md
├── db.sqlite3
├── manage.py
├── requirements.txt
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── account/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_initial.py
│   │   └── 0003_alter_onboardingtoken_options_and_more.py
│   ├── services/
│   │   ├── assistant_service.py
│   │   ├── ativation_service.py
│   │   ├── client_service.py
│   │   ├── onboarding_service.py
│   │   ├── organization_service.py
│   │   ├── professional_service.py
│   │   ├── token_service.py
│   │   └── user_service.py
│   ├── templates/
│   │   └── accounts/
│   └── urls/
│       ├── __init__.py
│       ├── auth.py
│       └── management.py
│
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── filters.py
│   ├── forms.py
│   ├── managers.py
│   ├── middleware.py
│   ├── tests.py
│   ├── config/
│   │   └── menus.py
│   ├── enums/
│   │   ├── account.py
│   │   ├── financial.py
│   │   ├── permissions.py
│   │   ├── scheduling.py
│   │   └── system.py
│   ├── management/
│   │   └── commands/
│   ├── menu/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── context_processors.py
│   │   └── registry.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── module.py
│   │   ├── organization_module.py
│   │   ├── permission.py
│   │   ├── role.py
│   │   ├── role_permission.py
│   │   └── tenant.py
│   ├── services/
│   │   └── context_service.py
│   ├── templates/
│   │   └── core/
│   ├── urls/
│   │   └── tenant.py
│   ├── utils/
│   │   └── uploads.py
│   └── views/
│       ├── __init__.py
│       ├── base.py
│       ├── dashboard.py
│       └── post_login.py
│
├── financial/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
│
├── scheduling/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
│
├── shared/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
│
├── website/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   └── templates/
│       └── website/
│
├── workout/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       └── __init__.py
│
├── static/
│   ├── css/
│   │   ├── base/
│   │   ├── components/
│   │   ├── pages/
│   │   └── vendor/
│   ├── img/
│   └── js/
│       ├── modules/
│       └── vendor/
│
└── templates/
    ├── base.html
    ├── base_app.html
    ├── base_auth.html
    ├── base_website.html
    ├── components/
    │   ├── form-select.html
    │   ├── form_date.html
    │   ├── form_field.html
    │   ├── form_file.html
    │   ├── form_switch.html
    │   ├── form_textarea.html
    │   └── modal_delete_confirm.html
    └── partials/
        ├── _alerts.html
        ├── _footer_public.html
        ├── _navbar_public.html
        └── _sidebar.html



---

## 👤 Model: User (`account/models/user.py`)

- User customizado com `AbstractBaseUser` + `PermissionsMixin`
- Login por **email** (não por username)
- Campos: `email`, `first_name`, `last_name`, `phone`, `is_active`, `is_staff`
- Manager customizado: `UserManager`

---

## 🏢 Model: Organization (`account/models/organization.py`)

- Representa uma empresa/clínica no sistema
- Campos: `company_name`, `slug`, `document`, `email`, `phone`, `is_active`
- Slug usado nas URLs como tenant: `/org/{slug}/...`

---

## 👥 Model: OrganizationMember (`account/models/organization_member.py`)

- Vincula **User ↔ Organization**
- Campo `roles` = ManyToMany com `core.Role`
- Campo `is_active` para desativar membro sem deletar
- Constraint: `unique_together(user, organization)`
- **Cliente NÃO tem membership** (acesso global)

---

## 📦 Model: Module (`core/models/module.py`)

- Representa um módulo do sistema (funcionalidade contratável)
- Campos: `slug`, `name`, `is_core`
- `is_core=True` → liberado automaticamente ao ativar org
- `is_core=False` → contratável (ativado sob demanda)

### Módulos planejados:

| Slug | Nome | Core? |
|---|---|---|
| `dashboard` | Dashboard | ✅ Sim |
| `clients` | Clientes | ✅ Sim |
| `professionals` | Profissionais | ✅ Sim |
| `settings` | Configurações | ✅ Sim |
| `schedule` | Agenda | ❌ Contratável |
| `financial` | Financeiro | ❌ Contratável |
| `physiotherapy` | Fisioterapia | ❌ Contratável |
| `psychology` | Psicologia | ❌ Contratável |
| `personal` | Personal Trainer | ❌ Contratável |
| `nutrition` | Nutrição | ❌ Contratável |
| `reports` | Relatórios | ❌ Contratável |

---

## 🏷️ Model: OrganizationModule (`account/models/organization_module.py`)

- Vincula **Organization ↔ Module**
- Campos: `organization`, `module`, `is_active`, `activated_at`
- Constraint: `unique_together(organization, module)`
- Módulos core são vinculados automaticamente ao ativar a org

---

## 🎭 Model: Role (`core/models/role.py`)

- Papéis do sistema (globais, não por org)
- Campos: `name`, `codename`, `level`, `description`

| Codename | Nome | Nível |
|---|---|---|
| `OWNER` | Proprietário | 100 |
| `ADMIN` | Administrador | 80 |
| `PROFESSIONAL` | Profissional | 50 |
| `ASSISTANT` | Assistente | 30 |
| `CLIENT` | Cliente | 10 |

---

## 🔐 Model: Permission (`core/models/permission.py`)

- Permissões vinculadas a um módulo
- Campos: `module` (FK), `codename`, `name`
- Constraint: `unique_together(module, codename)`
- Padrão por módulo: `view_`, `add_`, `edit_`, `delete_`

---

## 🔗 Model: RolePermission (`core/models/role_permission.py`)

- Vincula **Role ↔ Permission**
- Define quais permissões cada role tem
- Constraint: `unique_together(role, permission)`

### Mapa de permissões por Role:

| Permissão | OWNER | ADMIN | PROFESSIONAL | ASSISTANT | CLIENT |
|---|---|---|---|---|---|
| `view_dashboard` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `view_client` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `add_client` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `edit_client` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `delete_client` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_professional` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `add_professional` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `edit_professional` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `delete_professional` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_settings` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `edit_settings` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_schedule` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `add_schedule` | ✅ | ✅ | ✅ | ✅ | ❌ |
| `edit_schedule` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `delete_schedule` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_financial` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `add_financial` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `edit_financial` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `delete_financial` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_physiotherapy` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `add_physiotherapy` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `edit_physiotherapy` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `delete_physiotherapy` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_psychology` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `add_psychology` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `edit_psychology` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `delete_psychology` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_personal` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `add_personal` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `edit_personal` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `delete_personal` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_nutrition` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `add_nutrition` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `edit_nutrition` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `delete_nutrition` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `view_report` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `add_report` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `delete_report` | ✅ | ✅ | ❌ | ❌ | ❌ |

> **OWNER** = `__all__` (recebe todas automaticamente)

---

## 🚀 Provisionamento de Organização

### Signal (`account/signals.py`)
- Dispara em `post_save` do `Organization`
- Se org foi criada E está ativa → chama `provision_organization()`

### Service (`core/services/org_provisioning.py`)

#### `provision_organization(org)`
- Vincula todos os módulos `is_core=True` à org
- Cria `OrganizationModule` para cada módulo core
- Chamado automaticamente pelo signal

#### `activate_module_for_org(org, module_slug)`
- Ativa um módulo contratável para uma org
- Cria ou reativa `OrganizationModule`
- Chamado quando a org contrata um módulo

#### `deactivate_module_for_org(org, module_slug)`
- Desativa um módulo da org (não deleta)
- Seta `is_active=False` no `OrganizationModule`

---

## 🌱 Seeds (Management Commands)

### Ordem de execução:
```bash
python manage.py seed_all
# Executa na ordem:
# 1. seed_roles           → 5 Roles
# 2. seed_modules         → 4 core + 7 contratáveis + permissões
# 3. seed_role_permissions → vincula permissions às roles


Usuário loga
    │
    ├── É superuser?
    │   └── SIM → /admin-panel/
    │
    ├── Tem membership ativa em org?
    │   ├── 1 org  → /org/{slug}/dashboard/
    │   └── N orgs → última acessada ou primeira
    │
    └── Sem membership (CLIENTE)
        └── /portal/dashboard/ (dados globais, cross-org)


| Tipo | Membership? | Acesso | Destino |
| --- | --- | --- | --- |
| Superuser | N/A | Painel admin do sistema | /admin-panel/ |
| Owner/Admin | Sim | Dashboard da org | /org/{slug}/dashboard/ |
| Professional | Sim | Dashboard da org (limitado) | /org/{slug}/dashboard/ |
| Assistant | Sim | Dashboard da org (limitado) | /org/{slug}/dashboard/ |
| Cliente | Não | Portal global (seus dados) | /portal/dashboard/ |

Particularidade do Cliente:
NÃO depende de organização
NÃO tem OrganizationMember
Acessa dados dele em todas as orgs
Ex: agendamentos, históricos, sessões — independente de qual org criou
🛡️ Middleware Tenant (core/middleware/tenant.py)
Extrai org_slug da URL
Carrega Organization e seta em request.organization
Valida se org está ativa
Valida se usuário é membro ativo da org
🖥️ Painel Superuser — Gerenciamento de Módulos
CRUD de Módulos (sem mexer em código)
Listar: /admin-panel/modules/ → tabela com todos os módulos
Criar: /admin-panel/modules/novo/ → form + permissões inline
Editar: /admin-panel/modules/{slug}/editar/ → atualiza módulo e permissões
Funcionalidades:
Criar novo módulo com slug, nome, flag is_core
Adicionar permissões inline (codename + nome)
Visualizar badge CORE vs CONTRATÁVEL
Contador de permissões por módulo
Arquivos:
View: core/views/module_management.py
Form: core/forms/module_forms.py
URLs: core/urls/module_urls.py
Templates: core/templates/core/modules/module_list.html, module_form.html
🔄 Checagem de Acesso (Fluxo nas Views)

Request chega na view de um módulo
    │
    ├── 1. Usuário está logado? (LoginRequiredMixin)
    ├── 2. Middleware: org existe e está ativa?
    ├── 3. Middleware: usuário é membro ativo da org?
    ├── 4. Org tem o módulo ativo? (OrganizationModule.is_active)
    └── 5. Role do usuário tem a permission necessária? (RolePermission)
        │
        ├── TUDO OK → Acesso liberado ✅
        └── FALHOU  → 403 Forbidden ❌


✅ Checklist de Progresso
Feito:
 Model User customizado (login por email)
 Model Organization
 Model OrganizationMember (com roles M2M)
 Model Module (core vs contratável)
 Model OrganizationModule
 Model Role (5 níveis hierárquicos)
 Model Permission (vinculada a módulo)
 Model RolePermission (role ↔ permission)
 Seed de Roles (seed_roles)
 Seed de Modules + Permissions (seed_modules)
 Seed de RolePermissions (seed_role_permissions)
 Seed unificado (seed_all)
 Service de provisionamento de org
 Service de ativar/desativar módulo por org
 Signal de provisionamento automático
 Post-login redirect (superuser / staff / cliente)
 Middleware tenant
 Portal do cliente (acesso global, sem org)
 CRUD de Módulos (painel superuser)
 Template base (base.html, base_app.html)

Pendente:
 Dashboard da org (tenant)
 Dashboard do admin (superuser)
 CRUD de Organizações (painel superuser)
 Ativação/desativação de módulos por org (tela)
 Tela de seletor de organização (multi-org)
 Checagem de permissão nas views (decorator/mixin)
 CRUD de membros da org
 Testes automatizados
 Sistema de autenticação completo (login/logout/registro)
