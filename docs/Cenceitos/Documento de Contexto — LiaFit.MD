# 📐 LiaFit — Estrutura do Projeto

> Documento de referência da arquitetura e organização de arquivos.
> Stack: Django 4.2 LTS + SQLite + Design System próprio (Lia Linda).

---

## 🧱 Stack Técnica

| Categoria | Tecnologia |
|---|---|
| Framework | Django 4.2.30 (LTS) |
| Banco de Dados | SQLite |
| Frontend | Templates Django + CSS próprio (Lia Linda) + Bootstrap 5 (modais/utilitários) |
| Ícones | Lucide Icons |
| Fonte | Inter |
| Filtros | django-filter 25.1 |
| Rate Limit | django-ratelimit 4.1.0 |
| Imagens | Pillow 11.3.0 |
| Variáveis | python-dotenv 1.2.2 |

---

## 🗂️ Árvore de Diretórios


---

## 🧩 Apps Django

### `config/`
Configuração raiz do projeto. Contém `settings.py` e `urls.py` principal que inclui as rotas dos demais apps via namespaces.

### `account/`
App de **identidade e organizações**. Responsável por:
- Modelo de usuário customizado (`User`)
- Organizações (tenants) e seus membros
- Perfis (Owner, Professional, Client)
- Onboarding (registro, ativação por e-mail, magic links)
- Autenticação (login, logout, reset de senha)
- Gestão de equipe (members) e clientes

### `core/`
App de **infraestrutura compartilhada**. Responsável por:
- Modelos abstratos base (`BaseModel`, `TenantModel`)
- Sistema de permissões (Module, ModuleItem, Permission, Role, RolePermission)
- System Roles (papéis globais como SaaS Staff)
- Catálogo de módulos do SaaS (OrganizationModule)
- Bootstrap services (provisionamento inicial)
- Menu/sidebar dinâmica baseada em permissões
- Forms, filters e views base para reuso
- Dashboard do tenant
- Páginas de erro

### `saas_admin/`
App do **painel administrativo SaaS** (super admin). Acessado via prefixo `/painel/` e protegido pelo `SaaSAdminRequiredMixin`. Atualmente em fase inicial.

### `website/`
App do **site público** (landing page). Rotas sem autenticação para apresentação do produto.

---

## 🛣️ Roteamento (Namespaces)

| Namespace | Origem | Prefixo URL | Responsabilidade |
|---|---|---|---|
| `website` | `website/urls.py` | `/` | Site público |
| `auth` | `account/urls/auth_url.py` | `/auth/` | Login, registro, reset de senha |
| `tenant` | `core/urls/tenant_url.py` | `/app/` | Área autenticada do tenant |
| `master` | `core/urls/master_url.py` | `/master/` | Painel master/admin |
| `saas_admin` | `saas_admin/urls.py` | `/painel/` | Painel SaaS Admin |

---

## 🗃️ Modelagem de Dados

### Identidade
- **`User`** — usuário do sistema (e-mail como username)
- **`Organization`** — tenant / empresa (com `slug` para subdomínio)
- **`OrganizationMember`** — relação User ↔ Organization (M2M com role)

### Perfis
- **`OwnerProfile`** — dono da organização
- **`ProfessionalProfile`** — profissional/colaborador
- **`ClientProfile`** — cliente final
- **`Specialty`** — especialidades dos profissionais
- **`Client`** — modelo de cliente vinculado à organização

### Permissões
- **`Module`** — módulo do sistema (ex: Agenda, Clientes, Financeiro)
- **`ModuleItem`** — item dentro de um módulo (ex: Agenda → Calendário)
- **`Permission`** — permissão granular (item + action)
- **`Role`** — papel dentro de uma organização
- **`RolePermission`** — permissões atribuídas a um papel
- **`UserPermission`** — permissão direta a usuário (override)
- **`SystemRole`** — papel global do sistema (ex: SaaS Staff)
- **`UserSystemRole`** — atribuição de role global a usuário

### Catálogo
- **`OrganizationModule`** — quais módulos cada organização tem ativos

### Tokens
- **`OnboardingToken`** — tokens assinados para fluxos de onboarding (ativação, convite, reset de senha)

---

## 🔐 Sistema de Permissões

Hierarquia: **Module → ModuleItem → Permission**

- Permissões são atribuídas a **Roles** (por organização) via `RolePermission`
- Usuários recebem permissões via **OrganizationMember.role**
- Permissões diretas via `UserPermission` (override individual)
- Permissões globais (cross-tenant) via `SystemRole` + `UserSystemRole`

Verificação centralizada em `core/services/permission_service.py`.

---

## 🎨 Design System "Lia Linda"

Prefixo de classes: **`lia-*`**

### Estrutura CSS


### Tokens principais (`variables.css`)

| Categoria | Variáveis |
|---|---|
| Cores marca | `--color-primary`, `--color-secondary` (+ hover, light, border) |
| Cores feedback | `--color-success`, `--color-danger`, `--color-warning`, `--color-info` |
| Cores neutras | `--color-bg`, `--color-surface`, `--color-border`, `--color-text-*` |
| Tipografia | `--font-family` (Inter), `--font-size-xs` a `--font-size-3xl`, `--font-weight-*` |
| Espaçamento | `--space-1` (4px) a `--space-12` (48px) |
| Bordas | `--radius-sm/md/lg/xl/full` |
| Sombras | `--shadow-sm/md/lg` |
| Transições | `--transition-fast/base/slow` |
| Layout | `--sidebar-width: 260px`, `--sidebar-collapsed-width: 72px`, `--header-height: 64px`, `--content-max-width: 1200px` |

### Tema escuro
Suporte preparado via `[data-theme="dark"]` no `<html>`.

---

## 🧬 Templates Base

| Template | Uso |
|---|---|
| `base.html` | Template raiz (HTML, head, scripts comuns) |
| `base_app.html` | Layout da área autenticada (sidebar + header + conteúdo) |
| `base_auth.html` | Layout das telas de autenticação (split form + hero) |

### Blocos disponíveis
- `{% block title %}` — título da página
- `{% block meta %}` — meta tags extras
- `{% block page_css %}` — CSS específico da página
- `{% block page_content %}` — conteúdo principal
- `{% block page_js %}` — JS específico da página
- `{% block header_title %}` — título no header (apenas em `base_app.html`)

### Componentes reutilizáveis (`templates/components/`)
- `form_field.html` — campo de input com label, ícone e erros
- `form_select.html` — select estilizado
- `form_switch.html` — toggle switch
- `form_textarea.html` — textarea
- `form_date.html` — campo de data
- `form_file.html` — upload de arquivo
- `modal_delete_confirm.html` — modal de confirmação de exclusão

### Partials (`templates/partials/`)
- `_sidebar.html` — menu lateral dinâmico (renderiza menu baseado em permissões)
- `_alerts.html` — renderização de Django Messages como toasts

---

## ⚙️ Middlewares Customizados

Localizados em `core/middleware.py`. Responsáveis por:
- Resolução do tenant atual (via subdomínio/slug)
- Injeção do contexto de organização na request

---

## 🌐 Context Processors

| Processor | Origem | Função |
|---|---|---|
| `core.context_processors` | `core/context_processors.py` | Variáveis globais (`APP_NAME`, `APP_DOMAIN`, organização atual) |
| `core.menu.context_processors` | `core/menu/context_processors.py` | Menu da sidebar dinâmico |

---

## 🔧 Management Commands

| Comando | Função |
|---|---|
| `python manage.py bootstrap_core` | Provisiona catálogo, módulos, permissões e roles do sistema |
| `python manage.py check_catalog` | Valida integridade do catálogo de módulos/permissões |

---

## 📦 Padrão de Camadas


- **Views** apenas orquestram (recebem request, chamam services, devolvem response)
- **Services** concentram regras de negócio e operações de domínio
- **Forms** fazem validação de entrada
- **Filters** (django-filter) para listagens com query params
- **Models** apenas dados e métodos triviais
- **Bootstrap services** isolam provisionamento inicial

---

## 🎟️ Fluxos de Onboarding

Gerenciados por `account/services/onboarding_service.py` + `token_service.py`.

| Fluxo | Origem | Ação |
|---|---|---|
| Cadastro de empresa | `register.html` | Cria User + Organization + envia link de ativação |
| Ativação de conta | `setup_password.html` | Define senha e ativa o usuário |
| Convite de membro | `accept_invite.html` | Aceita convite e define senha |
| Reset de senha | `password_reset_request.html` → `password_reset_done.html` | Envia link de redefinição |
| E-mail já existe | `_modal_email_exists_confirm.html` | Vincula nova empresa a conta existente |
| Link inválido | `setup_password_invalid.html` | Estado de erro para tokens expirados |

---

## 📋 Convenções

- **Idioma**: Português (Brasil) na UI, inglês no código
- **Nomes de arquivos**: `snake_case` em Python, `kebab-case` em CSS, `_underscore` para partials Django
- **Classes CSS**: BEM com prefixo `lia-` (`.lia-card__header--active`)
- **Imports**: agrupados (stdlib → Django → terceiros → projeto)
- **Strings de UI**: envolvidas em `{% translate %}` ou `{% blocktranslate %}` (i18n)
- **IDs no HTML**: `kebab-case`
- **Form fields no Django**: `snake_case`

Nunca implementar código direto. 

Ser cirúrgico, nada de codificar ao acaso.

Se não entender algo pergunte ou pede arquvivos não chute nada.
