## 🎯 Visão Geral
LiaFit é um SaaS multi-tenant nas áreas de saúde, beleza e bem-estar. Não é só academia, não é só personal, não é só nutrição — é tudo ao mesmo tempo, num sistema modular.

Stack: Django + arquitetura multi-tenant por organização (sem schema separado — tenant por FK).

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
Cliente é global: um cliente pode ser atendido por várias orgs ao mesmo tempo e vê tudo dele agregado.
Organização só enxerga clientes vinculados via OrganizationClient.
Profissional pode trabalhar em várias orgs e ter vários papéis na mesma org.

## 🧱 Sistema de Módulos

| Model | Função |
| --- | --- |
| Module | Feature do sistema (ex: Dashboard, Agenda, Financeiro, Psicologia). |
| ModuleItem | Sub-item/tela de um módulo. É o que vira entrada de menu. |
| OrganizationModule | Quais módulos a org contratou. |


### Módulo Core vs. Contratado
Module.is_core = True → ativo automaticamente em toda org nova
Module.is_core = False → precisa ser contratado via OrganizationModule

### 🆕 Campo scope em Module
Define o "mundo" em que o módulo aparece:

superuser → área admin global do LiaFit
global → área do cliente (menu pessoal, vê tudo dele agregado)
tenant → dentro de uma organização (profissionais/assistentes)

### 🆕 Campo owner em ModuleItem
FK opcional pra Module. Permite desacoplar grupo visual da regra de contratação:

module = grupo visual onde o item aparece no menu (ex: "Cadastros")
owner = módulo que controla a disponibilidade (ex: "Financeiro")
Se owner = null → module controla ambos
Ex: item "Fornecedor" aparece no grupo "Cadastros" (core), mas só se a org contratou "Financeiro" (owner).

## 🔐 Sistema de Permissões

| Model | Função |
| --- | --- |
| Permission | Ação (view/add/change/delete) sobre um ModuleItem. Identificada por codename. |
| Role | Papel dentro de uma org (tenant). Tem level (hierarquia numérica). |
| RolePermission | Permissões atribuídas a um papel. |
| OrganizationMember.roles | N:N — papéis do membro naquela org. |
| UserPermission | Override individual por usuário (allow/deny). |


### Resolução de permissões
User.get_permission_codenames(organization) retorna o set final de codenames.

Superuser → todas
Sem org → set vazio
Com org → codenames via roles ativas do membership
(UserPermission ainda não está integrado à resolução — TODO)

## 📋 Regra de Visibilidade do Menu
Para cada ModuleItem, ele aparece se todas as condições baterem:

Scope bate com o contexto atual (superuser / global / tenant)
Módulo e item ativos (is_active e show_in_menu em ambos)
Disponibilidade do módulo (só scope tenant):
controlador = item.owner OR item.module
controlador.is_core = True OU org tem OrganizationModule ativo
Permissão do usuário:
Superuser → libera
Scope tenant → checa view_<route_base> em get_permission_codenames(org)
Scope global (cliente) → sem checagem de permissão (visibilidade implícita). Segurança dos dados fica nas queries das views, filtrando por OrganizationClient.user.
Scope superuser → só is_superuser

## 🧭 Contexto de Request (request.context)
Middleware já existente (em ajustes) que injeta no request:

ctx.organization — org atual (scope tenant)
ctx.modules — módulos disponíveis na org
ctx.permissions — codenames do usuário naquela org
(usado pelo builder de menu e pelas views)

## 📐 Convenções Técnicas
TenantModel (abstrato)
Todo model tenant-aware herda de TenantModel, que força:

FK obrigatória para Organization
Manager customizado (TenantManager) com for_tenant()

### Rotas
ModuleItem.route_base = slug.replace('-', '_')
url_name(action) → tenant:<route_base>_<action> (ex: tenant:supplier_list)
SPECIAL_MENU_ROUTES → exceções para rotas fora do padrão

### Codenames de permissão
Formato: <action>_<route_base> (ex: view_supplier, add_client)
Devem ser consumidos como constantes em core/constants/permissions.py para evitar typos

### Constantes (🆕 a criar)

core/
  constants/
    __init__.py
    permissions.py   → Perms.VIEW_SUPPLIER, ADD_CLIENT, ...
    modules.py       → Modules.CORE, Modules.FINANCIAL, ...
    scopes.py        → Scopes.SUPERUSER, Scopes.GLOBAL, Scopes.TENANT

## 🛣️ Roadmap Atual
✅ Models de account, módulos, permissões consolidados
✅ Adicionar Module.scope + ModuleItem.owner (migration)
✅ Criar core/constants/
⏳ Refatorar builder do menu para o fluxo acima (hoje é híbrido → passa 100% pro banco)
⏳ Integrar UserPermission na resolução de permissões

## 🚨 Pontos de Atenção
Cliente nunca vê dados de outro cliente. Filtro por OrganizationClient.user = request.user.client_profile em toda query do scope global.
Cliente vê dados agregados de todas as orgs que o atendem — não filtrar por org no scope global.
owner pode ser null — nesse caso o próprio module controla disponibilidade.
Soft-delete em OrganizationClient via archived_at — usar all_objects para incluir arquivados.


## 📝 Contexto atualizado — Sistema de Permissões LiaFit

### ✅ Fase 1 concluída
module_item.py — imports limpos, permission_codename() retorna {module_slug}.{action}_{item_slug}, UniqueConstraint em (module, slug)
permission.py — codename sempre regenerado no save, max_length=200
### ✅ Fase 2 concluída
core/constants/ virou pacote com catalog.py + menu_routes.py + __init__.py
Apagado catalogy.py (nome errado)
MODULES agora tem scope (tenant/global/superuser) e suporta owner_slug em items
ROLES agora tem scope (tenant/global/superuser)
2 módulos novos: my-area (global) e saas-admin (superuser)
2 roles novos: client (global) e platform_admin (superuser)
Criado SystemRole (não herda de TenantModel, permissions M2M direto)
Criado UserSystemRole (atribuição user ↔ system_role com timestamps)
bootstrap.py refatorado com 3 funções:
sync_system_catalog() — modules + items + perms (com owner em 2ª passada)
sync_system_roles() — cria SystemRoles (global + superuser)
bootstrap_organization(org) — só tenant (módulos core + roles + owner)
_resolve_permissions() com scope_filter pra isolar permissões por escopo
## 🗂️ Arquitetura de permissões consolidada

┌─ TENANT (dentro da org) ──────────────────┐
│  Role ── RolePermission ── Permission     │
│  User ── OrganizationMember.roles ── Role │
└───────────────────────────────────────────┘

┌─ GLOBAL / SUPERUSER (fora da org) ────────┐
│  SystemRole.permissions (M2M) ── Permission│
│  User ── UserSystemRole ── SystemRole     │
└───────────────────────────────────────────┘


### 🎯 Padrão de codename
{module_slug}.{action}_{item_slug} → ex: clients.view_client, saas-admin.change_billing

## 📦 Estrutura final de arquivos

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


