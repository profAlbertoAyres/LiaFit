# LiaFit — Contexto Completo do Projeto (Memória do Agente)

> **Como usar:** Anexe este arquivo ao iniciar uma nova conversa com o agente "Programador Django - Beto". Ele contém todo o contexto arquitetural, decisões tomadas e status atual do projeto LiaFit.

**Última atualização:** 16/04/2026
**Mantenedor:** Alberto (desenvolvedor + professor de Programação Web)
**Versão do blueprint:** v2 (fundação estratégica aprovada)

---

## 👤 Identificação do Desenvolvedor

- **Nome:** Alberto
- **Localização:** Cacoal - RO, Brasil
- **Timezone:** America/Porto_Velho
- **Perfil:** Professor de Programação Web + desenvolvedor do LiaFit
- **Natureza do projeto:** Produto real + material didático (explicações com "porquê" são bem-vindas)

---

## 🎯 Visão Geral do Projeto

**LiaFit** é um SaaS **multi-tenant** para gestão de academias, estúdios e clínicas de atividade física.

### Conceitos-chave

- Cada **empresa** (academia/clínica/estúdio) é um **tenant** isolado (`Organization`)
- Um mesmo **usuário** pode ser **cliente** e/ou **profissional** em várias empresas
- **Dados globais do user** (nome, email, CPF, foto, telefone) são compartilhados entre empresas vinculadas
- **Dados operacionais** (fichas, agenda, prontuário, financeiro) são **estritamente isolados por `organization_id`**
- Empresa só enxerga dado global de cliente **se houver vínculo ativo**

### Stack

- **Backend:** Django 5.x + DRF
- **DB:** PostgreSQL (prod) / SQLite (dev)
- **Auth:** JWT (SimpleJWT) + Session (admin Django)
- **Front MPA:** Templates Django + CSS BEM (prefixo `lia-`) + JS vanilla
- **Docs API:** drf-spectacular (Swagger/Redoc)
- **Locale:** pt-BR (com i18n preparado via `gettext_lazy`)
- **Timezone:** America/Porto_Velho

---

## 🏛️ Princípios Arquiteturais (Regras de Ouro)

### 1. Separação de Responsabilidades

| Camada | Responsabilidade | NÃO faz |
|--------|------------------|---------|
| Models | Estrutura de dados, validações de campo, `__str__`, `get_absolute_url` | Regra de negócio, orquestração, envio de email |
| Services | Regra de negócio, orquestração multi-model, `@transaction.atomic`, integrações | Render, acesso a `request` |
| Forms/Serializers | Validação de entrada, coerção de tipos, mensagens de erro | Persistência, chamar services pesados |
| Views | Request → Service → Response | Lógica de negócio, queries complexas |
| Templates | Apresentação HTML | Lógica além de exibição |
| URLs | Roteamento | Qualquer outra coisa |

**Regra prática:** view com mais de 15-20 linhas de lógica → extrai para service.

### 2. Models "burros", Services "inteligentes"

- Models só guardam e validam estrutura
- Services orquestram operações multi-model com `@transaction.atomic`
- Ex: criar User + Organization + Member + Token → é `OnboardingService.register`, NÃO método no model

### 3. Internacionalização

- **Codenames internos:** inglês (`OWNER`, `ADMIN`, `SCHEDULING`)
- **Labels de UI:** PT-BR, envoltos em `gettext_lazy` quando aplicável
- **Slugs:** inglês quando possível
- Nunca usar `name` (PT-BR) para lógica — sempre `codename`

### 4. CSS / Nomenclatura

- Prefixo **`lia-`** em TODAS as classes
- Padrão BEM: `lia-bloco__elemento--modificador`
- Exemplos: `lia-auth__form-side`, `lia-btn--primary`, `lia-form-control--error`

### 5. Multi-tenancy

- **Tenant atual** resolvido via **URL** (`/org/<slug>/...`) por middleware `TenantMiddleware`
- Arquitetura **preparada para migrar para subdomínio** (`academia-x.liafit.com`) sem refactor profundo
- Todo model operacional tem FK obrigatória para `Organization` (indexada)
- Manager customizado (`TenantManager`) força filtro por organization

### 6. Isolamento de Dados (LGPD)

- **Dados globais** (no `User`): compartilhados entre empresas vinculadas
- **Dados operacionais** (por empresa): isolados por `organization_id`
- Empresa só acessa dado global se houver `OrganizationClient` ou `OrganizationMember` ativo

---

## 📦 Estrutura de Apps

```
LiaFit/
├── config/              # settings, urls raiz, wsgi/asgi
├── core/                # BaseModel, Role, TenantManager
├── account/             # User, Organization, Member, Client, Onboarding
├── modules/             # catálogo de módulos vendáveis
├── billing/             # contratação de módulos (futuro)
├── api/                 # camada DRF
├── templates/
│   ├── base.html        # visitante (marketing)
│   ├── base_app.html    # logado (único para todos os perfis)
│   └── partials/
└── static/              # CSS, JS, vendor
```

---

## 🗃️ Modelo de Dados

### `BaseModel` (abstract — core)

```python
id: UUIDField (PK)
created_at: DateTimeField (auto_now_add)
updated_at: DateTimeField (auto_now)
is_active: BooleanField (default=True)
```

### `Role` (core)

| Campo | Tipo | Observação |
|-------|------|------------|
| codename | CharField único | EN: OWNER, ADMIN, ... |
| name | CharField | PT-BR: "Proprietário", ... |
| level | IntegerField | hierarquia numérica |

**Seed (data migration):**

| codename | name | level |
|----------|------|-------|
| OWNER | Proprietário | 100 |
| ADMIN | Administrador | 80 |
| PROFESSIONAL | Profissional | 50 |
| ASSISTANT | Assistente | 30 |
| CLIENT | Cliente | 10 |

### `User` (account)

| Campo | Tipo | Observação |
|-------|------|------------|
| email | EmailField único | USERNAME_FIELD |
| full_name | CharField | |
| phone | CharField | blank |
| cpf | CharField | blank |
| birth_date | DateField | null |
| photo | ImageField | blank |
| **is_active** | BooleanField | "pode ser operado no sistema" |
| **email_verified_at** | DateTimeField | null — "dono do email confirmou" |
| is_staff | BooleanField | admin Django |

**Regra de login:** `is_active=True` **E** `has_usable_password()=True`
`email_verified_at` NÃO bloqueia login — é informativo.

### `Organization` (account)

| Campo | Tipo |
|-------|------|
| name | CharField (razão social) |
| slug | SlugField único |
| document | CharField (CNPJ/CPF) |
| phone | CharField |
| email | EmailField |
| owner | FK → User (PROTECT) |
| is_active | BooleanField (default=False) |

### `OrganizationMember` (account) — staff da empresa

| Campo | Tipo |
|-------|------|
| organization | FK → Organization |
| user | FK → User |
| roles | M2M → Role |
| is_active | BooleanField |

**Constraint:** `unique_together(organization, user)`

### `OrganizationClient` (account) — cliente da empresa

| Campo | Tipo |
|-------|------|
| organization | FK → Organization |
| user | FK → User |
| created_by | FK → User (quem cadastrou) |
| welcome_email_sent | BooleanField |
| first_service_at | DateTimeField (null) |
| notes | TextField (blank) |
| is_active | BooleanField |

**Constraint:** `unique_together(organization, user)`

### `OnboardingToken` (account)

| Campo | Tipo |
|-------|------|
| user | FK → User |
| token | UUIDField único |
| expires_at | DateTimeField |
| used_at | DateTimeField (null) |

### `Module` (modules)

```python
codename: CharField único (EN)    # "SCHEDULING", "FINANCE"
name: CharField (PT-BR)
description: TextField
price_monthly: DecimalField
dependencies: M2M → Module (self)
is_active: BooleanField
```

### `OrganizationModule` (modules)

```python
organization: FK → Organization
module: FK → Module
contracted_at: DateTimeField
cancelled_at: DateTimeField (null)
is_active: BooleanField
```

---

## 🔄 Fluxos Críticos

### Onboarding da Empresa (2 etapas)

**Etapa 1 — Registro público** (`/account/register/`)

Campos: `full_name`, `email`, `organization_name`.

```
OnboardingService.register():
  @transaction.atomic
  1. Cria User (is_active=False, set_unusable_password)
  2. Cria Organization (is_active=False, slug gerado)
  3. Cria OrganizationMember (role OWNER)
  4. Gera OnboardingToken (24h validade)
  5. Envia email com link /account/setup-password/<token>/
```

**Etapa 2 — Setup via token** (`/account/setup-password/<token>/`)

Campos: senha + confirmação (obrigatórios), phone, cpf, org_phone (opcionais).

```
OnboardingService.setup_password():
  @transaction.atomic
  1. Valida token (existe, não usado, não expirado)
  2. Define senha do user
  3. Atualiza campos complementares
  4. User.is_active = True
  5. User.email_verified_at = now()
  6. Organization.is_active = True
  7. Token.used_at = now()
  8. Redireciona para login
```

### Cadastro de Cliente pela Empresa

**Cenário A — Cliente novo (email não existe):**

```
ClientService.create_for_organization(organization, data, notify_email):
  @transaction.atomic
  1. Cria User (is_active=True, email_verified_at=None, senha inutilizável)  # "shadow client"
  2. Cria OrganizationClient
  3. Se notify_email=True → envia email de boas-vindas com link pra definir senha
```

**Cenário B — Cliente já existe no sistema:**

```
1. Sistema detecta User com esse email
2. Exibe aviso: "Cliente já existe. Confirme com ele antes de vincular."
3. Se empresa confirma → cria apenas OrganizationClient (não toca no User)
```

### Auto-cadastro do Cliente

Cliente se cadastra espontaneamente → User nasce com `is_active=False` até validar email via token.

---

## 🎨 Camada de Apresentação (MPA)

### Layouts — apenas 2

| Template | Público |
|----------|---------|
| `base.html` | Visitantes (marketing) |
| `base_app.html` | Todos os logados (único) |

> `base_auth.html` será renomeado para `base_app.html` (mais semântico).

### Sidebar Dinâmica (regra consolidada)

```
[1] 👤 MINHA CONTA → sempre visível

[2] 🏃 ÁREA DO CLIENTE (GLOBAL, NÃO filtra por empresa)
    → Visível se user tem ≥ 1 OrganizationClient
    → Agrega dados de TODAS as empresas onde é cliente
    → Itens: agendamentos, histórico, empresas onde sou cliente

[3] 🏢 EMPRESA ATUAL (CONTEXTUAL, filtra pela empresa selecionada)
    → Visível se user tem ≥ 1 OrganizationMember
    → Dropdown lista empresas onde é membro
    → Itens baseados no ROLE do user na empresa selecionada
    → Itens filtrados pelos MÓDULOS contratados pela empresa
```

**Regra crítica:**
- Parte de **CLIENTE é global** (visão consolidada, nunca filtra)
- Parte de **PROFISSIONAL/EMPRESA é contextual** (sempre filtra pela empresa)
- Mesmo user pode ser cliente + profissional da mesma empresa → ambos os blocos aparecem

---

## 🌐 Camada API (DRF)

### Auth
- JWT (SimpleJWT) para clientes (mobile/SPA) — `Authorization: Bearer <token>`
- Session para admin Django

### Endpoints principais

| Método | Rota | Auth |
|--------|------|------|
| POST | `/api/auth/login/` | pública |
| POST | `/api/auth/refresh/` | pública |
| GET | `/api/auth/me/` | JWT |
| POST | `/api/onboarding/register/` | pública |
| POST | `/api/onboarding/setup-password/` | pública |
| GET | `/api/orgs/` | JWT |
| GET/PATCH | `/api/orgs/{slug}/` | JWT |
| GET/POST | `/api/orgs/{slug}/members/` | JWT |
| GET/POST | `/api/orgs/{slug}/clients/` | JWT |
| POST | `/api/orgs/{slug}/activate/` | JWT (OWNER) |
| GET | `/api/roles/` | JWT |
| GET | `/api/modules/` | JWT |
| GET | `/api/docs/` + `/api/redoc/` | pública |

### Permissions customizadas
- `IsOrganizationActive`
- `HasRoleAtLeast` (com `required_level`)
- `ReadOnlyOrRoleAtLeast`
- `IsOrganizationMember`

---

## 💰 Modelo Comercial (Decisão: Opção A)

- **Venda avulsa**: cada módulo tem preço próprio
- Dependências automáticas: contratar "Academia" → inclui "Agendamento" com preço somado
- **Sem bundles/planos no MVP** (escalar depois se necessário)

---

## 🔒 Backup & Exportação

- **Backup de infraestrutura:** responsabilidade operacional da LiaFit (fora do escopo do produto)
- **Exportação por empresa:** feature **futura** (pós-MVP), atende LGPD/portabilidade em caso de encerramento

---

## 🗺️ Roadmap de Implementação

### Sprint 1 — Fundação do Onboarding ⚡ (EM ANDAMENTO)
- [ ] Data migration: seed dos 5 Roles
- [ ] Ajustar `Organization.is_active` default=False
- [ ] Adicionar `email_verified_at` no User
- [ ] `account/forms.py` (Register + SetupPassword)
- [ ] `account/services/` (user, organization, token, onboarding)
- [ ] Views: register, setup_password
- [ ] `account/urls.py`
- [ ] Adaptar `register.html`
- [ ] Criar `setup_password.html`
- [ ] Envio de email (console backend em dev)

### Sprint 2 — Multi-tenancy & Navegação
- [ ] `TenantMiddleware` (resolve organization pela URL)
- [ ] Renomear `base_auth.html` → `base_app.html`
- [ ] Sidebar dinâmica (3 blocos)
- [ ] Seletor de empresa atual

### Sprint 3 — Clientes (OrganizationClient)
- [ ] Model + migrations
- [ ] Services (cliente novo, cliente existente)
- [ ] Views: cadastro pela empresa, listagem, detalhes
- [ ] Auto-cadastro de cliente

### Sprint 4 — API REST
- [ ] DRF + SimpleJWT + drf-spectacular
- [ ] Serializers, permissions, views
- [ ] Swagger/Redoc

### Sprint 5 — Módulos & Billing
- [ ] Model Module + OrganizationModule
- [ ] Catálogo, contratação, dependências
- [ ] Filtro de menu baseado em módulos contratados

### Sprint 6 — Gestão de Membros
- [ ] Convites por email
- [ ] Alteração de roles, remoção

### Sprint 7 — Domínio Operacional
- [ ] Agendamento, fichas, prontuário (por módulo)

### Sprint 8 — Produção
- [ ] Email real, rate limiting, CORS restrito
- [ ] Logs, observabilidade
- [ ] Testes de isolamento entre tenants
- [ ] Export de dados por empresa
- [ ] Deploy

---

## ✅ Status Atual (16/04/2026)

### Pronto
- [x] Models base: `BaseModel`, `Role`, `User`, `Organization`, `OrganizationMember`, `OnboardingToken`
- [x] User manager customizado (email como login)
- [x] Templates: `base.html`, `base_auth.html`, `login.html`, `register.html` (antiga), partials
- [x] CSS com prefixo `lia-`
- [x] Configuração básica (settings, urls)

### Próximo passo imediato
**Sprint 1 — começar pela Etapa 1:** ajustes no model `User` (adicionar `email_verified_at` + migration).

---

## 🤖 Instruções de Comportamento do Agente

### Papel
Par de programação sênior em Django/DRF, mentor didático. Alberto é professor e dev — explica o **porquê** das decisões.

### Sempre
- Respeitar arquitetura: Models burros, Services orquestram, Views finas
- Usar `@transaction.atomic` em operações multi-model
- Codenames em inglês, labels em PT-BR
- Prefixo `lia-` em todo CSS
- Pedir para ver arquivos existentes antes de criar novos
- Entregar código em blocos organizados por etapa
- Numerar entregas multi-etapa (ETAPA 1, ETAPA 2...)
- Finalizar com próximo passo ou validação
- Responder em PT-BR, com Markdown + code blocks

### Nunca
- Gerar tudo de uma vez sem validar contexto
- Sugerir mudanças radicais de arquitetura sem discutir
- Inventar campos de model sem confirmar schema
- Adivinhar em dúvidas de escopo → perguntar
- Usar bibliotecas externas sem necessidade clara
- Escrever lógica em template além de exibição
- Misturar inglês em labels de UI (só em codenames internos)
- Colocar regra de negócio em views ou models

---

## 📋 Glossário

| Termo | Significado |
|-------|-------------|
| Tenant | Cliente isolado — aqui é `Organization` |
| Onboarding | Cadastro inicial em 2 etapas |
| Role | Papel funcional com nível numérico |
| Membership | Vínculo `User ↔ Organization` (staff) |
| OrganizationClient | Vínculo `User ↔ Organization` (cliente) |
| Shadow Client | Cliente criado pela empresa, nunca acessou o sistema |
| Setup Token | UUID enviado por email para definir senha |
| Service | Classe com regra de negócio, orquestra models |
| MPA | Multi-Page Application (templates Django) |
| Codename | Identificador interno em inglês (ex: `OWNER`) |
| BEM | Block-Element-Modifier (padrão CSS) |

---

## 📜 Histórico de Decisões Importantes

| # | Decisão | Opção escolhida |
|---|---------|-----------------|
| 1 | Onboarding em 2 etapas (email antes de senha) | Confirmado |
| 2 | `is_active` do User = operacional; `email_verified_at` = validação | A (dois campos separados) |
| 3 | Cadastro de cliente pela empresa (shadow client) | Permitido, `is_active=True` direto |
| 4 | Modelo comercial dos módulos | A (avulso, sem bundles no MVP) |
| 5 | Resolução de tenant | URL no MVP, preparado para subdomínio |
| 6 | Backup interno | Responsabilidade da LiaFit (infra) |
| 7 | Exportação de dados por empresa | Feature futura (pós-MVP) |
| 8 | Layouts de navegação | 2 layouts (público + logado único) |
| 9 | Sidebar logado | Cliente global + Empresa contextual |
| 10 | Filtro de menu de empresa | Por role + módulos contratados |

---

---

## 🧩 Papéis e Vínculos: Regras Canônicas

> Seção adicionada em 16/04/2026 após discussão arquitetural.
> Esta seção consolida decisões sobre **como papéis (`Role`) se relacionam com vínculos** (`OrganizationMember` e `OrganizationClient`).

### Catálogo de Roles

O modelo `Role` contém **todos** os papéis possíveis no sistema:

| codename | name (PT-BR) | level | Atribuído via |
|----------|--------------|-------|---------------|
| `OWNER` | Proprietário | 100 | `OrganizationMember.roles` |
| `ADMIN` | Administrador | 80 | `OrganizationMember.roles` |
| `PROFESSIONAL` | Profissional | 50 | `OrganizationMember.roles` |
| `ASSISTANT` | Assistente | 30 | `OrganizationMember.roles` |
| `CLIENT` | Cliente | 10 | **`OrganizationClient`** (implícito no vínculo) |

### Regra de Ouro

> **`Role.CLIENT` existe no catálogo, mas NUNCA é atribuído via `OrganizationMember.roles`.**
> A condição de "ser cliente de uma organização" materializa-se pela **existência de um `OrganizationClient`** ativo, não por uma linha em `Member`.

### Separação por natureza do vínculo

| Tabela | Natureza | Roles aceitos | Campos específicos |
|--------|----------|---------------|---------------------|
| `OrganizationMember` | Vínculo **staff** (funcional) | OWNER, ADMIN, PROFESSIONAL, ASSISTANT (M2M — pode combinar) | — |
| `OrganizationClient` | Vínculo **cliente** (consumidor) | CLIENT (implícito, não persistido como FK) | `first_service_at`, `welcome_email_sent`, `notes`, `created_by` |

### Regras operacionais

1. **Múltiplos roles em `Member`**: um mesmo `OrganizationMember` pode ter vários roles simultâneos (ex: `[OWNER, PROFESSIONAL]` — dono que também dá aula).
2. **`OWNER` é exclusivo por organização**: apenas o `Organization.owner` pode ter esse role. Validar no service.
3. **`CLIENT` bloqueado em Member**: validar no `clean()` do `OrganizationMember` que o role CLIENT não seja atribuído. Se tentar, levantar `ValidationError`.
4. **Todo Member deve ter no mínimo 1 role**: validação no service de criação.
5. **Cliente é natureza global do User**: um `User` pode existir sem nenhum vínculo, ou ser cliente de 1+ organizações. O vínculo nasce no primeiro atendimento (ou cadastro proativo pela empresa — "shadow client").

### 🔑 Padrão Canônico: Um User, Múltiplos Vínculos na Mesma Organização

Um mesmo `User` pode ter, **simultaneamente na mesma `Organization`**:

- 1 `OrganizationMember` com 1+ roles (atuando como staff)
- 1 `OrganizationClient` (consumindo serviço como cliente)

**Exemplo canônico:**
> Dra. Marina é **nutricionista** (profissional) da clínica "Corpo & Mente" e, na **mesma clínica**, é **cliente** do psicólogo para fazer terapia.

```python
# Dois vínculos distintos, coexistindo sem conflito:
OrganizationMember(user=marina, organization=clinica, roles=[PROFESSIONAL])
OrganizationClient(user=marina, organization=clinica, first_service_at=...)


**FIM DO DOCUMENTO DE CONTEXTO**
