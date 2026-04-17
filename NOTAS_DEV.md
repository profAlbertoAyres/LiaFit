# LiaFit — Contexto do Agente de Desenvolvimento

> **Versão:** 2.1
> **Última atualização:** 17/04/2026
> **Mantenedor:** Alberto
> **Propósito:** Fonte única de verdade para o agente "Programador Django - Beto" e para o próprio Alberto consultar decisões arquiteturais, schema e roadmap.

---

## 📜 Histórico de Versões

| Versão | Data | Mudanças principais |
|--------|------|---------------------|
| 1.0 | 10/03/2026 | Blueprint inicial |
| 2.0 | 16/04/2026 | Blueprint v2 aprovado — multi-tenant consolidado, ciclo de vida do User, shadow client |
| **2.1** | **17/04/2026** | **Refatoração do `account/models.py` concluída: perfis Professional/Client/Assistant como extensões 1:1; OnboardingToken consolidado; soft-delete via archived_at** |

---

## 🎯 Visão do Produto

**LiaFit** é um SaaS multi-tenant para gestão de academias, estúdios de pilates, clínicas de atividade física e profissionais autônomos da área de saúde/movimento.

**Proposta de valor:** uma plataforma única onde:
- A **empresa** gerencia agenda, fichas, financeiro, comunicação
- O **profissional** acompanha seus clientes, agenda, prescrições
- O **cliente final** vê seus agendamentos, fichas, pagamentos, **de todas as empresas em que é cliente**, num só login

**Tese central:** um mesmo CPF/email pode estar em múltiplos papéis em múltiplas empresas. O sistema precisa tratar isso como cidadão de primeira classe desde o dia 1.

---

## 🧱 Stack Técnica

| Camada | Tecnologia |
|--------|------------|
| Backend | Django 5.x + Django REST Framework |
| DB Prod | PostgreSQL |
| DB Dev | SQLite |
| Autenticação | JWT (SimpleJWT) para API + Session (admin Django) |
| Frontend | Templates Django (MPA) + CSS BEM com prefixo `lia-` + JS vanilla |
| Documentação API | drf-spectacular (Swagger + Redoc) |
| Locale | pt-BR |
| Timezone | America/Porto_Velho |
| Storage de arquivos | Local (dev) / S3-compatible (prod, futuro) |

---

## 🏛️ Regras de Ouro (NÃO NEGOCIÁVEIS)

### Separação de Responsabilidades

| Camada | Responsabilidade | NÃO faz |
|--------|------------------|---------|
| **Models** | Estrutura, validações de campo, `__str__`, `@property` de leitura simples | Regra de negócio, orquestração, acesso a `request` |
| **Services** | Regra de negócio, `@transaction.atomic`, operações multi-model | Render, acesso direto a `request` |
| **Forms/Serializers** | Validação de entrada | Persistência, lógica pesada |
| **Views** | Request → Service → Response | Lógica de negócio, queries complexas |
| **Templates** | HTML | Lógica além de exibição |

**Regra prática:** view com > 15-20 linhas de lógica → extrai para service.

### Convenções de Nomenclatura

- **Codenames internos (DB, Python):** inglês — `OWNER`, `ADMIN`, `SCHEDULING`
- **Labels de UI:** PT-BR (preparado para `gettext_lazy` no futuro)
- **CSS:** prefixo `lia-` + BEM → `lia-bloco__elemento--modificador`
- **Multi-tenant:** tenant resolvido via URL (`/org/<slug>/...`) no MVP. Arquitetura preparada para subdomínio futuro.
- **Todo model operacional:** FK obrigatória indexada para `Organization` (via `TenantModel`)

### Padrões de FK ao User

- **`on_delete=PROTECT`** em todos os FKs para `User` (exceto auto-deleção cascateada legítima, como tokens)
- **Razão:** User nunca é deletado; ações destrutivas passam por serviço de desativação/arquivamento

---

## 📦 Estrutura de Apps

```
core/       → BaseModel, TenantModel, Role, TenantManager, enums, utils
account/    → User, Organization, OrganizationMember, OrganizationClient,
              Professional, Client, Assistant, OnboardingToken
modules/    → Module, OrganizationModule (catálogo vendável)
api/        → camada DRF (serializers, viewsets, permissions)
```

---

## 🗃️ Modelo de Dados (schema atual)

### Arquitetura em camadas

```
User (pessoa global — dados compartilhados)
 ├── memberships → OrganizationMember ──┬── professional_profile → Professional
 │                   (vínculo staff)     └── assistant_profile   → Assistant
 │
 └── client_links → OrganizationClient ──── client_profile       → Client
                     (vínculo cliente)
```

**Princípio fundamental:**
- `User` = **pessoa** (dados globais, compartilhados entre empresas)
- `OrganizationMember` / `OrganizationClient` = **vínculo** com a empresa (contém dados do relacionamento)
- `Professional` / `Assistant` / `Client` = **perfil funcional** (dados específicos do papel dentro daquele vínculo)

### 📌 `BaseModel` (abstract, em `core`)

Todo model herda de `BaseModel`:

```python
id          : UUIDField(primary_key=True)
created_at  : DateTimeField(auto_now_add=True)
updated_at  : DateTimeField(auto_now=True)
is_active   : BooleanField(default=True)
```

### 📌 `TenantModel` (abstract, em `core`)

Models operacionais (que "pertencem" a uma empresa) herdam também de `TenantModel`, que injeta:

```python
organization : ForeignKey(Organization, on_delete=CASCADE, db_index=True)
```

E fornece o manager `TenantManager` para filtragem por tenant.

### 📌 `Role` (em `core`)

Catálogo de papéis do sistema. Seed obrigatório:

| codename (EN) | name (PT-BR) | level |
|---------------|--------------|-------|
| OWNER | Proprietário | 100 |
| ADMIN | Administrador | 80 |
| PROFESSIONAL | Profissional | 50 |
| ASSISTANT | Assistente | 30 |
| CLIENT | Cliente | 10 |

### 📌 `User` (em `account`)

Herda de `AbstractUser`. Login por **email** (sem username).

**Campos globais:**
- `email` (unique, USERNAME_FIELD)
- `cpf`, `phone`, `photo`
- `birth_date`, `gender` (choices via `core.enums.account.Gender`)
- `emergency_contact`, `emergency_phone`
- `email_verified_at` (DateTimeField, null=True) — **NÃO bloqueia login, é informativo**
- `is_active` (herdado, controla login)
- Campos herdados: `first_name`, `last_name`, `password`, `date_joined`

**Estados lógicos (combinações de campos):**

| Estado | `is_active` | `email_verified_at` | Senha usável |
|--------|-------------|---------------------|--------------|
| Auto-registro pendente | `False` | `None` | Não |
| Shadow Client | `True` | `None` | Não |
| User Completo | `True` | `<datetime>` | Sim |
| Suspenso | `False` | `<datetime>` | Sim |

**Properties utilitárias (leitura):**
- `is_email_verified` → bool
- `is_shadow` → bool (shadow client ativo sem validação)

**Regra de login:**
```
login_ok = is_active == True AND has_usable_password() == True
```

### 📌 `Organization` (em `account`)

Tenant do sistema.

**Campos:**
- `name`, `slug` (unique), `document` (CNPJ/CPF), `phone`, `email`
- `is_active` (default=**False**) — ativada na Etapa 2 do onboarding
- `owner` → FK User, `on_delete=PROTECT`, `null=True` (permitido só por ordem de criação na transaction; service sempre preenche)

### 📌 `OrganizationMember` (em `account`)

Vínculo STAFF entre User e Organization.

**Campos:**
- `user` → FK User (PROTECT)
- `organization` → FK Organization (CASCADE)
- `roles` → M2M Role (um membro pode ter múltiplos papéis)
- `is_active` (bool)

**Constraint:** `unique(user, organization)`

**Regra:** role `CLIENT` NUNCA é atribuído aqui. Para ser cliente, usa `OrganizationClient`.

### 📌 `OrganizationClient` (em `account`)

Vínculo CLIENTE entre User e Organization.

**Campos:**
- `user` → FK User (PROTECT)
- `organization` → FK Organization (CASCADE)
- `created_by` → FK User (SET_NULL) — quem cadastrou (shadow) ou `null` (auto-cadastro)
- `first_service_at` (DateTimeField, null) — preenchido no 1º agendamento
- `welcome_email_sent` (bool)
- `notes` (TextField) — observações internas da empresa
- `archived_at` (DateTimeField, null) — **soft-delete**, preserva histórico

**Managers:**
- `objects` → `ActiveClientManager` (filtra `archived_at__isnull=True`)
- `all_objects` → todos, inclusive arquivados (auditoria)

**Constraint:** `unique(user, organization)`

**Regra:** desvínculo NUNCA deleta — apenas preenche `archived_at`.

### 📌 `Professional` (em `account`)

Perfil do profissional. Extensão **1:1 com `OrganizationMember`**.

Herda `TenantModel` + `BaseModel`.

**Campos exclusivos:**
- `member` → OneToOne OrganizationMember (CASCADE)
- `specialty` (str)
- `registration_type` (ex: CREF, CRP, CRN, CREFITO)
- `registration_number` (str)
- `bio` (text)

### 📌 `Client` (em `account`)

Perfil do cliente. Extensão **1:1 com `OrganizationClient`**.

Herda `TenantModel` + `BaseModel`.

**Por que 1:1 com OrganizationClient e não com User?**
→ O objetivo muda de contexto. Mesma pessoa pode ter "hipertrofia" na academia e "reabilitação" na clínica.

**Campos exclusivos:**
- `organization_client` → OneToOne OrganizationClient (CASCADE)
- `objective` (text) — objetivo do cliente naquela empresa

### 📌 `Assistant` (em `account`)

Perfil do assistente/recepcionista. Extensão **1:1 com `OrganizationMember`**.

Herda `TenantModel` + `BaseModel`.

**Campos exclusivos:**
- `member` → OneToOne OrganizationMember (CASCADE)
- `department` (str)

### 📌 `OnboardingToken` (em `account`)

Token de uso único para fluxos de ativação de conta.

**Usos previstos:**
- Setup de senha do owner (registro de empresa) — **Sprint 1**
- Validação de email do auto-registro de cliente — **Sprint 3**

**Campos:**
- `user` → FK User (CASCADE)
- `token` → UUIDField (unique, default=uuid4, não editável)
- `expires_at` (DateTimeField) — default: 24h
- `used_at` (DateTimeField, null) — timestamp de uso (preserva auditoria)

**Properties:**
- `is_used` → bool
- `is_expired` → bool
- `is_valid` → bool (`not is_used and not is_expired`)

**Nota técnica (N5):** no futuro, avaliar unificação com tokens de reset de senha e troca de email num único `UserToken` com campo `purpose`.

---

## 🔄 Fluxos Críticos

### 1. Onboarding de empresa (2 etapas)

**Etapa 1 — Registro público** (`POST /register/`)
1. Usuário preenche: email, nome da empresa, CNPJ
2. `OnboardingService.register()` (atomic):
   - Cria `User(is_active=False, email_verified_at=None)` sem senha
   - Cria `Organization(is_active=False, owner=user)`
   - Cria `OrganizationMember(user, organization)` com role OWNER
   - Cria `OnboardingToken(user, expires_at=now+24h)`
   - Enfileira email de setup de senha

**Etapa 2 — Setup de senha** (`GET/POST /setup-password/<token>/`)
1. Valida token (`is_valid`)
2. `OnboardingService.setup_password(token, password)` (atomic):
   - Define senha do user
   - `user.is_active = True`
   - `user.email_verified_at = now()`
   - `organization.is_active = True`
   - `token.used_at = now()`
3. Login automático + redirect para dashboard da empresa

### 2. Cadastro de cliente pela empresa

**Caso A — Cliente novo (email não existe no sistema):**
1. Empresa preenche form com email + dados mínimos
2. `ClientService.create_by_org(org, data)` (atomic):
   - Cria `User(is_active=True, email_verified_at=None)` sem senha (**shadow**)
   - Cria `OrganizationClient(user, org, created_by=current_member)`
   - Cria `Client(organization_client, objective=...)` se objetivo informado

**Caso B — Email já existe:**
1. Sistema detecta e pede confirmação ao operador
2. Se confirmado: cria apenas `OrganizationClient` + `Client` (reaproveita User)
3. **Nenhum dado global do User é alterado**

### 3. Auto-registro de cliente (Sprint 3)

1. Cliente se cadastra com email
2. Cria `User(is_active=False, email_verified_at=None)` + `OnboardingToken`
3. Email de validação
4. Ao clicar no link: ativa conta, define senha, `email_verified_at=now()`

### 4. Desvinculação de cliente

`ClientService.archive(organization_client)`:
- Preenche `archived_at = now()`
- **NÃO deleta** agendamentos, pagamentos, fichas
- Cliente desaparece das listagens normais, permanece em relatórios históricos

---

## 🎨 Navegação (MPA)

### Layouts

Apenas **2 layouts**:
- `base.html` → visitante (login, registro, páginas públicas)
- `base_app.html` → logado (único, com sidebar dinâmica)

### Sidebar Dinâmica (3 blocos)

1. **Minha Conta** — sempre visível
   - Perfil, senha, preferências

2. **Área do Cliente** — **GLOBAL e consolidada**
   - Mostra dados de TODAS as empresas em que o user é cliente
   - NUNCA filtra por empresa selecionada
   - Visível apenas se o user tem ao menos 1 `OrganizationClient` ativo

3. **Empresa Atual** — **CONTEXTUAL**
   - Filtra pela empresa selecionada no seletor do topo
   - Itens dinâmicos baseados em:
     - Papéis do membro naquela empresa (`OrganizationMember.roles`)
     - Módulos contratados (`OrganizationModule`)

---

## 💰 Modelo Comercial

- Módulos **avulsos** (sem bundles no MVP)
- **Dependências automáticas:** contratar um módulo inclui automaticamente suas dependências (ex: "Academia" inclui "Agendamento"), com preço somado
- Cobrança por organização (não por usuário)
- Trial inicial: a definir

---

## 🗺️ Roadmap — Sprints

### ✅ Sprint 0 — Fundação (concluída)
- Django project + apps estruturados
- `BaseModel`, `TenantModel`, `Role`
- Custom User com email
- Estrutura de templates e CSS base

### 🏗️ Sprint 1 — Fundação do Onboarding (EM ANDAMENTO)

**Status atual (17/04/2026):**
- ✅ `account/models.py` refatorado e validado
- ⏳ Migrations pendentes
- ⏳ Seed de Roles
- ⏳ `OnboardingService.register()`
- ⏳ `OnboardingService.setup_password()`
- ⏳ Forms: `RegisterForm`, `SetupPasswordForm`
- ⏳ Views + URLs
- ⏳ Templates de registro e setup

**Próximo passo imediato:** validar `core/models/tenant.py` e gerar migrations.

### 🔜 Sprint 2 — Dashboard multi-empresa + seletor de org
### 🔜 Sprint 3 — Auto-registro de cliente + validação de email
### 🔜 Sprint 4 — Cadastro proativo de cliente (shadow) pela empresa
### 🔜 Sprint 5 — Catálogo de Módulos + contratação
### 🔜 Sprint 6 — Gestão de membros (convite, papéis, desativação)

---

## 🗒️ Notas Técnicas (decisões pendentes/futuras)

| # | Nota | Status |
|---|------|--------|
| N1 | Multi-tenant por URL (`/org/<slug>/`) no MVP; subdomínio no futuro | Decidido |
| N2 | Roles como M2M (não FK única) — um membro pode acumular papéis | Decidido |
| N3 | Validação de email separada do login (`email_verified_at` é informativo) | Decidido |
| N4 | Soft-delete via `archived_at` em `OrganizationClient` | **Implementado v2.1** |
| N5 | Unificar tokens (onboarding, reset senha, troca email) em `UserToken` com `purpose` | Pendente, pós-MVP |
| N6 | Estratégia de storage (S3) para `photo` e `avatar` | Pendente, pré-produção |
| N7 | Internacionalização (i18n) — labels já em PT-BR, marcar com `gettext_lazy` | Pendente, pós-MVP |
| N8 | Perfis (Professional, Client, Assistant) como extensão 1:1 do vínculo | **Decidido v2.1** |

---

## 🤖 Regras de Comportamento do Agente "Beto"

### SEMPRE
- Responder em PT-BR, Markdown + code blocks com linguagem
- Pedir para ver arquivos existentes antes de criar novos
- Entregar código em etapas numeradas
- Usar `@transaction.atomic` em operações multi-model
- Explicar o **porquê** das decisões (projeto é didático)
- Finalizar com próximo passo ou pergunta de validação
- Consultar este documento como fonte primária

### NUNCA
- Gerar tudo de uma vez sem validar contexto
- Sugerir mudanças radicais de arquitetura sem discutir
- Inventar campos de model — confirmar schema aqui antes
- Adivinhar em dúvidas de escopo — perguntar
- Colocar regra de negócio em views ou models
- Misturar inglês em labels de UI (só em codenames internos)
- Escrever lógica em template além de exibição

---

**Fim do documento — v2.1**
