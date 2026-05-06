# 📘 Documento de Contexto — LiaFit

## 🎯 Visão Geral
LiaFit é um SaaS **marketplace multi-vertical** nas áreas de saúde, beleza e bem-estar. 
Não é só academia, não é só personal, não é só nutrição — é tudo ao mesmo tempo, num sistema modular.

**Conceito-chave:** O LiaFit é uma plataforma onde **múltiplas empresas distintas** 
(academias, clínicas, studios, personals, nutricionistas, psicólogos…) operam de forma 
independente. Os **Admins SaaS** administram a **plataforma**, não as empresas. Eles são 
operadores transversais, sem vínculo com nenhuma organização cliente.

Uma mesma pessoa física (`User`) pode acumular papéis ortogonais:
- 👑 Admin SaaS (opera a plataforma)
- 💼 Membro de organização (trabalha numa empresa cliente)
- 🏃 Cliente global (é atendido por uma ou mais organizações)

**Stack:** Django + arquitetura multi-tenant por organização (sem schema separado — tenant por FK).

---

## 🏗️ Arquitetura de Domínio

### Entidades principais

| Entidade | Papel |
| --- | --- |
| User | Usuário global. Não pertence a org diretamente. Pode ser superuser, profissional, assistente ou cliente. |
| Organization | Empresa que contrata o LiaFit. Tem owner (dono) e members. |
| OrganizationMember | Vínculo de trabalho: usuário trabalha em uma org. N:N com Role. Um usuário pode ter múltiplos vínculos (várias orgs) e múltiplos papéis na mesma org. |
| Professional | Perfil profissional atrelado a um OrganizationMember (CREF, CRP, CRN, etc.). |
| Assistant | Perfil de assistente atrelado a um OrganizationMember. |
| Client | Perfil de cliente. Global — não pertence a nenhuma org. |
| OrganizationClient | Vínculo de atendimento entre Client e Organization. Suporta arquivamento (soft-delete preserva histórico). |
| OnboardingToken | Tokens para onboarding, reset senha, magic link, convite, etc. |

### Regras-chave
- Cliente é global: um cliente pode ser atendido por várias orgs ao mesmo tempo e vê tudo dele agregado.
- Organização só enxerga clientes vinculados via OrganizationClient.
- Profissional pode trabalhar em várias orgs e ter vários papéis na mesma org.
- Admin SaaS **transcende organizações** — não tem `current_organization` no contexto.

---

## 🧱 Sistema de Módulos

| Model | Função |
| --- | --- |
| Module | Feature do sistema (ex: Dashboard, Agenda, Financeiro, Psicologia). |
| ModuleItem | Sub-item/tela de um módulo. É o que vira entrada de menu. |
| OrganizationModule | Quais módulos a org contratou. |

### Módulo Core vs. Contratado
- `Module.is_core = True` → ativo automaticamente em toda org nova
- `Module.is_core = False` → precisa ser contratado via OrganizationModule

### Campo `scope` em Module
Define o "mundo" em que o módulo aparece:
- `superuser` → área admin global do LiaFit
- `global` → área do cliente (menu pessoal, vê tudo dele agregado)
- `tenant` → dentro de uma organização (profissionais/assistentes)

### Campo `owner` em ModuleItem
FK opcional pra Module. Permite desacoplar grupo visual da regra de contratação:
- `module` = grupo visual onde o item aparece no menu (ex: "Cadastros")
- `owner` = módulo que controla a disponibilidade (ex: "Financeiro")
- Se `owner = null` → `module` controla ambos
- Ex: item "Fornecedor" aparece no grupo "Cadastros" (core), mas só se a org contratou "Financeiro" (owner).

---

## 🔐 Sistema de Permissões

| Model | Função |
| --- | --- |
| Permission | Ação (view/add/change/delete) sobre um ModuleItem. Identificada por codename. |
| Role | Papel dentro de uma org (tenant). Tem level (hierarquia numérica). |
| RolePermission | Permissões atribuídas a um papel. |
| OrganizationMember.roles | N:N — papéis do membro naquela org. |
| UserPermission | Override individual por usuário (allow/deny). |
| SystemRole | Papel global ou superuser (fora do tenant). Permissions M2M direto. |
| UserSystemRole | Atribuição user ↔ system_role com timestamps. |

### Resolução de permissões
`User.get_permission_codenames(organization)` retorna o set final de codenames.
- Superuser → todas
- Sem org → set vazio
- Com org → codenames via roles ativas do membership
- (UserPermission ainda não está integrado à resolução — TODO)

### Arquitetura consolidada

```text
┌─ TENANT (dentro da org) ──────────────────┐
│  Role ── RolePermission ── Permission     │
│  User ── OrganizationMember.roles ── Role │
└───────────────────────────────────────────┘

┌─ GLOBAL / SUPERUSER (fora da org) ─────────┐
│  SystemRole.permissions (M2M) ── Permission│
│  User ── UserSystemRole ── SystemRole      │
└────────────────────────────────────────────┘
```

### Padrão de codename
`{module_slug}.{action}_{item_slug}` → ex: `clients.view_client`, `saas-admin.change_billing`

---

## 📋 Regra de Visibilidade do Menu
Para cada ModuleItem, ele aparece se todas as condições baterem:
1. Scope bate com o contexto atual (superuser / global / tenant)
2. Módulo e item ativos (`is_active` e `show_in_menu` em ambos)
3. Disponibilidade do módulo (só scope tenant):
   - controlador = `item.owner OR item.module`
   - `controlador.is_core = True` OU org tem `OrganizationModule` ativo
4. Permissão do usuário:
   - Superuser → libera
   - Scope tenant → checa `view_<route_base>` em `get_permission_codenames(org)`
   - Scope global (cliente) → sem checagem de permissão (visibilidade implícita). Segurança dos dados fica nas queries das views, filtrando por `OrganizationClient.user`.
   - Scope superuser → só `is_superuser`

---

## 🧭 Contexto de Request (`request.context`)
Middleware que injeta no request:
- `ctx.organization` — org atual (scope tenant)
- `ctx.modules` — módulos disponíveis na org
- `ctx.permissions` — codenames do usuário naquela org
- (usado pelo builder de menu e pelas views)

---

## 📐 Convenções Técnicas

### TenantModel (abstrato)
Todo model tenant-aware herda de `TenantModel`, que força:
- FK obrigatória para Organization
- Manager customizado (`TenantManager`) com `for_tenant()`

### Rotas
- `ModuleItem.route_base = slug.replace('-', '_')`
- `url_name(action)` → `tenant:<route_base>_<action>` (ex: `tenant:supplier_list`)
- `SPECIAL_MENU_ROUTES` → exceções para rotas fora do padrão

### Codenames de permissão
- Formato: `{module_slug}.{action}_{item_slug}` (ex: `clients.view_client`)
- Devem ser consumidos como constantes em `core/constants/`

---

## 📦 Estrutura final de arquivos (core)

```text
core/
├── constants/
│   ├── __init__.py       ← re-exporta
│   ├── catalog.py        ← MODULES, ROLES, DEFAULT_ACTIONS
│   └── menu_routes.py    ← SPECIAL_MENU_ROUTES
├── models/
│   ├── base.py
│   ├── tenant.py
│   ├── module.py                ← com scope
│   ├── module_item.py           ← com owner + codename corrigido
│   ├── organization_module.py
│   ├── permission.py            ← codename auto-regenerado
│   ├── role.py                  ← tenant only
│   ├── role_permission.py
│   ├── user_permission.py
│   ├── system_role.py           🆕 global/superuser
│   └── user_system_role.py      🆕 atribuição
└── bootstrap.py
```

### bootstrap.py — 3 funções
- `sync_system_catalog()` — modules + items + perms (com owner em 2ª passada)
- `sync_system_roles()` — cria SystemRoles (global + superuser)
- `bootstrap_organization(org)` — só tenant (módulos core + roles + owner)
- `_resolve_permissions()` com `scope_filter` pra isolar permissões por escopo

---

## 🎨 Design System LiaFit (Frontend)

### Stack
- **Bootstrap 5** como base
- **Design system próprio** com prefixo `lia-*` (BEM-style)
- **Lucide Icons** (`<i data-lucide="...">`)
- **Inter font** via Google Fonts
- **Bootstrap JS bundle** + módulos JS próprios
- **Flatpickr** pra datas (no contexto autenticado)

### Hierarquia de templates

```text
base.html (avô — head, fontes, CSS/JS globais)
├── base_app.html      ← áreas autenticadas (sidebar + header) ⭐
├── base_auth.html     ← login/cadastro (layout dividido)
└── base_website.html  ← site público (navbar + footer)
```

### Blocos disponíveis em `base_app.html`
- `{% block sidebar %}` → sobrescrever sidebar inteira
- `{% block header_title %}` → título no header
- `{% block header_actions %}` → ações no topo
- `{% block page_content %}` → conteúdo da página
- `{% block page_css %}` / `{% block page_js %}` → assets específicos

### Sidebar global (`partials/_sidebar.html`)
- Menu **dinâmico** via `sidebar_menu` no context
- Estrutura: `[{label, items: [{url, label, icon}]}]`
- Footer lê `request.context.membership.highest_role_name`
- **Assume contexto multi-tenant** — não serve diretamente pro SaaS Admin

### Header (`base_app.html`)
- Mostra seletor de organização **apenas se** `show_org_selector = True` no context
- No SaaS Admin: **não setamos** essa variável → seletor some automaticamente ✨

---

## 🛣️ Roadmap Geral
- ✅ Models de account, módulos, permissões consolidados
- ✅ Adicionar `Module.scope` + `ModuleItem.owner` (migration)
- ✅ Criar `core/constants/`
- ✅ `SystemRole` + `UserSystemRole` criados
- ⏳ Refatorar builder do menu para o fluxo acima (hoje é híbrido → passa 100% pro banco)
- ⏳ Integrar `UserPermission` na resolução de permissões

---

## 🚨 Pontos de Atenção
- Cliente nunca vê dados de outro cliente. Filtro por `OrganizationClient.user = request.user.client_profile` em toda query do scope global.
- Cliente vê dados agregados de todas as orgs que o atendem — não filtrar por org no scope global.
- `owner` pode ser null — nesse caso o próprio `module` controla disponibilidade.
- Soft-delete em `OrganizationClient` via `archived_at` — usar `all_objects` para incluir arquivados.

---

# 🛡️ Projeto: SaaS Admin (`/painel/`)

> Área administrativa global da plataforma LiaFit — exclusiva da equipe interna.
> Separada do Django Admin (`/admin/`) e do painel de cada tenant.

## 🎯 Objetivo
Criar uma área administrativa global onde a equipe SaaS LiaFit (Alberto + staff interno) possa:
- Visualizar todas as organizações da plataforma
- Acompanhar métricas globais (MRR, MAU, etc.)
- Gerenciar usuários globais
- Entrar em **modo suporte** dentro de uma org cliente (com auditoria)

Essa área é o ponto de partida para o fluxo de **suporte técnico controlado** — onde um operador SaaS pode entrar dentro de um tenant pra dar suporte, com tudo logado.

---

## 🧩 Decisões arquiteturais cravadas

| # | Decisão | Justificativa |
|---|---|---|
| 1 | App Django: **`saas_admin`** | Nome neutro, não conflita com `django.contrib.admin` |
| 2 | Localização do app: **raiz do projeto** (paralelo a `core/`, `account/`) | Padrão atual do projeto |
| 3 | URL prefix: **`/painel/`** ⚡ ATUALIZADO | Discrição — não revela natureza administrativa |
| 4 | Namespace URL: **`saas_admin`** | Ex: `{% url 'saas_admin:dashboard' %}` |
| 5 | Acesso protegido por **`SaaSAdminRequiredMixin`** ⚡ ATUALIZADO | Verifica `UserSystemRole` com scope=SUPERUSER + failsafe `is_superuser` |
| 6 | Template base SaaS Admin **estende `base_app.html`** ⚡ NOVO | Reusa 100% do design system LiaFit |
| 7 | Sidebar **isolada** em `templates/saas_admin/_sidebar.html` ⚡ NOVO | Não polui a sidebar global do tenant |
| 8 | Sidebar **estática (hardcoded)** na Fase 0 ⚡ NOVO | Sem dependência de `sidebar_menu` no context |
| 9 | **Badge "ADMIN"** ao lado do logo na sidebar ⚡ NOVO | Diferenciação visual sutil mas clara |
| 10 | Header reusa do `base_app`, **sem seletor de organização** | `show_org_selector` não é setado |
| 11 | **Zero CSS/JS novo** na Fase 0 ⚡ ATUALIZADO | Reusa tudo do design system existente |
| 12 | **Bloqueio total** de admins SaaS no fluxo tenant normal | Staff SaaS NÃO pode usar tenants comuns — só via "modo suporte" (Fase 2+) |
| 13 | **Modo Suporte** (Opção A.1) | Sessão temporária pra entrar como staff numa org cliente |
| 14 | Sessão de suporte = **4h** ou até logout | Expira automaticamente |
| 15 | Login **centralizado** em `auth:login` | Sem login separado para o saas_admin |
| 16 | Identidade visual: **a definir** ⚡ EM ABERTO | Decisão pra Fase 1+ (cor distintiva pro admin) |
| 17 | Modo suporte futuro: **vermelho** (`--color-danger`) | Estado visual distinto |

---

## 🧠 Conceito reforçado
- **Admin SaaS = operador da plataforma**, não dono de empresa
- A mesma pessoa pode ser: admin SaaS + membro de org + cliente global (papéis ortogonais)
- Sistema de permissões: `SystemRole`/`UserSystemRole` com `scope = "superuser"` (catálogo `saas-admin`)
- O acesso à área é via system role; permissões finas dentro dela podem ser refinadas via `SystemRole` futuramente

---

## 🗺️ Roadmap por fases

```text
🔜 Fase 0 → Esqueleto navegável /painel/             ← EM ANDAMENTO
   Fase 1 → Identidade visual distintiva (cor)
   Fase 2 → Middleware: bloquear admins SaaS no fluxo tenant
   Fase 3 → Modelo SupportSession (entrada/saída/log)
   Fase 4 → UX: botão "entrar como suporte" + sair
   Fase 5 → Polimentos (auditoria, expiração, alertas)
   Fase 6 → Gestão completa de Organizações (CRUD)
   Fase 7 → Gestão de Usuários globais
   Fase 8 → Métricas / Billing / Planos
```

---

## 📦 Fase 0 — Escopo

### O que será entregue
Esqueleto navegável e protegido, **sem lógica de negócio ainda**:
- Dashboard placeholder com **4 cards mockados** (orgs, usuários, clientes, novos 30d)
- Sidebar isolada com badge "ADMIN" e menu hardcoded
- Header reaproveitado do `base_app` (sem seletor de org)
- Bloqueio de acesso pra quem não é admin SaaS (403)

### Sidebar Fase 0 — itens hardcoded

```text
GERAL
  📊 Dashboard               ✅ funciona
  🏢 Clientes                # placeholder
  🏛️  Organizações           # placeholder

OPERAÇÃO
  💰 Financeiro              # placeholder
  📈 Métricas                # placeholder

SISTEMA
  📜 Logs                    # placeholder
  ⚙️  Configurações          # placeholder

FOOTER
  Nome do usuário
  "Admin SaaS · LiaFit"
  🚪 Sair → auth:logout
```

### Dashboard Fase 0 — 4 cards mockados

```text
┌─ 🏛️ Organizações ─┐ ┌─ 👥 Usuários ─┐ ┌─ 💼 Clientes ─┐ ┌─ 📈 Novos (30d) ─┐
│      42           │ │    1.234       │ │     87         │ │      +12         │
│   ativas          │ │  cadastrados   │ │  contratados   │ │   este mês       │
└───────────────────┘ └────────────────┘ └────────────────┘ └──────────────────┘
```

Valores hardcoded em `get_context_data`. Na Fase 1+ pluga queries reais.

---

## 📂 Lista de arquivos da Fase 0 (11 itens)

| # | Arquivo | Tipo | Responsabilidade |
|---|---|---|---|
| 1 | `saas_admin/__init__.py` | 🆕 vazio | Marca pacote |
| 2 | `saas_admin/apps.py` | 🆕 | AppConfig |
| 3 | `saas_admin/views/__init__.py` | 🆕 vazio | Marca subpacote |
| 4 | `saas_admin/views/base.py` | 🆕 | `SaaSAdminRequiredMixin` |
| 5 | `saas_admin/views/dashboard.py` | 🆕 | `DashboardView` com 4 cards mock |
| 6 | `saas_admin/urls.py` | 🆕 | `app_name="saas_admin"` |
| 7 | `templates/saas_admin/_sidebar.html` | 🆕 | Sidebar mockada com badge ADMIN |
| 8 | `templates/saas_admin/base.html` | 🆕 | Extends `base_app.html`, sobrescreve sidebar |
| 9 | `templates/saas_admin/dashboard.html` | 🆕 | 4 cards Bootstrap + classes `lia-*` |
| 10 | `config/settings.py` | ✏️ | Add `'saas_admin'` em `INSTALLED_APPS` |
| 11 | `config/urls.py` | ✏️ | Add `path('painel/', include('saas_admin.urls'))` |

**Smoke test final:** acessar `http://localhost:8000/painel/` logado como superuser → ver dashboard com sidebar do SaaS Admin com badge ADMIN visível.

---

## ⚠️ Pontos a confirmar/ajustar no código (Fase 0)
- Caminho do import do modelo `Organization` (provavelmente `core.models`?)
- Nome do campo de data de criação (`created_at`?)
- Namespace do logout — confirmado: **`auth:logout`** ✅
- Critério de acesso definido: **`UserSystemRole` scope=SUPERUSER + failsafe `is_superuser`** ✅
- `APP_NAME` no context (assumido como context processor existente)

---

## 🎨 Identidade visual — Fase 1+ (em aberto)
A questão de cor distintiva (chumbo vs vermelho vs índigo etc.) foi **adiada pra Fase 1**. 
Na Fase 0 o SaaS Admin usa o **mesmo design system** do tenant, com diferenciação **apenas pelo badge "ADMIN"** ao lado do logo na sidebar.

### Estados visuais previstos (futuro)

| Estado | Cor | Quando |
|---|---|---|
| 🟦 Tenant normal | Índigo (`--color-primary`) | Operação comum dos clientes |
| ⬛ SaaS Admin | A definir na Fase 1 | Dentro do `/painel/` |
| 🟥 Modo Suporte | Vermelho (`--color-danger`) | Dentro de uma org cliente em modo de suporte |

---

## 🎓 Modo de trabalho com a IA
- 👨‍🏫 **Contexto pessoal**: Alberto é professor e usa o projeto pra aprender/ensinar
- 🐢 **Ritmo**: um arquivo por vez, sem pressa
- 📚 **Didática**: explicação curta do "porquê" antes do código
- 📄 **Entrega**: arquivo inteiro no final, com indicação clara de onde colocar
- ❓ **Pausa pra dúvida**: avançar só após confirmação do Alberto
- 🌐 **Idioma**: Português (BR)
- 🤝 **Tom**: profissional + leve, com emojis pontuais
- 📍 **Localização**: Porto Velho (timezone America/Porto_Velho)

---

## 📍 Estado atual do SaaS Admin (snapshot pra retomada)
- ✅ Discovery completo (backend + frontend + design system)
- ✅ Todas as decisões arquiteturais cravadas e atualizadas
- ✅ Plano da Fase 0 aprovado (11 arquivos)
- ✅ Conceito de marketplace multi-vertical compreendido e documentado
- ✅ Arquitetura de templates entendida (`base_app.html` é o avô)
- 🔜 **Próximo passo concreto**: começar a Fase 0 pelo arquivo nº 1 (`saas_admin/__init__.py` — arquivo vazio)

---

## 🚀 Como retomar amanhã
1. Abrir nova conversa colando este documento como contexto
2. Dizer: *"Vamos retomar a Fase 0 do SaaS Admin a partir do passo 1"*
3. A IA vai entregar o `__init__.py` vazio com instruções de onde colocar
4. Confirmar e seguir os 11 passos sequencialmente

---

*Última atualização: 27/04/2026 — sessão de planejamento Fase 0 concluída.*
