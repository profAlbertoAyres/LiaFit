# LiaFit — Contexto do Agente de Desenvolvimento

> **Versão:** 2.1
> **Última atualização:** 17/04/2026
> **Mantenedor:** Alberto
> **Propósito:** Fonte única de verdade para o agente "Programador Django - Beto" e para o próprio Alberto consultar decisões arquiteturais, schema e roadmap.

---

## 📅 2026-04-18 — Sistema de Onboarding Tokens com Auditoria

### 🎯 Objetivo
Implementar infraestrutura robusta de tokens para fluxos de ativação de conta,
reset de senha, convites e verificação de email, com trilha de auditoria completa.

### ✅ Entregas

#### 1. Model `OnboardingToken` (account/models.py)
Model genérico de tokens com suporte a múltiplos propósitos via campo `purpose`.

**Campos principais:**
- `token` (UUID) — identificador único, gerado automaticamente
- `user` (FK) — dono do token
- `organization` (FK, nullable) — contexto organizacional (opcional)
- `purpose` (choices) — tipo do token (`onboarding`, `reset_password`, etc.)
- `expires_at` (datetime) — TTL do token
- `data` (JSONField) — payload extra flexível por purpose

**Auditoria — criação:**
- `created_ip` — IP de quem solicitou
- `created_ua` — User-Agent de quem solicitou

**Auditoria — uso:**
- `used_at` — quando foi consumido
- `used_ip` — IP de quem consumiu
- `used_ua` — User-Agent de quem consumiu

**Timestamps (via BaseModel):**
- `created_at`, `updated_at`

**Índice composto:** `(user, purpose, used_at)` para consultas rápidas.

#### 2. `TokenService` (account/services/token_service.py)
Serviço centralizado para ciclo de vida de tokens.

**Métodos:**
- `create_token(user, purpose, ttl, organization, ip, user_agent, data)` — cria token
- `get_valid_token(token_str, purpose=None)` — valida (existe, não expirado, não usado)
- `invalidate_token(token, ip, user_agent)` — marca como usado com auditoria

**Comportamento:**
- Levanta exceptions tipadas em caso de falha (ver abaixo)
- Validação de `purpose` opcional (para garantir token certo no fluxo certo)

#### 3. `OnboardingService` (account/services/onboarding_service.py)
Orquestra o cadastro completo de uma nova organização.

**Método principal:** `register_organization(user_data, org_data, ip, user_agent)`

**Fluxo:**
1. Cria `User` inativo (sem senha definida)
2. Cria `Organization` via `OrganizationService` (slug único garantido)
3. Gera `OnboardingToken` com purpose `ONBOARDING` (TTL 3 dias)
4. Dispara email de ativação (console em DEV)
5. Retorna a organização criada

#### 4. `OrganizationService` (refatorado)
- Geração de slug única e determinística (resolve colisões com sufixo numérico)
- Método `activate_organization(org)` para ativação pós-confirmação

#### 5. Exceptions tipadas (account/exceptions.py)
- `TokenExpiredError` — token fora da validade
- `TokenAlreadyUsedError` — tentativa de reuso
- `TokenInvalidError` — token inexistente/malformado
- `TokenPurposeMismatchError` — purpose errado para o fluxo

Permite tratamento granular nas views com mensagens específicas ao usuário.

#### 6. Admin (account/admin.py)
- `list_display` com token encurtado, status visual (🟢 válido / ⏱️ expirado / ✅ usado)
- Fieldsets organizados (Identificação / Validade / Auditoria Criação / Auditoria Uso / Metadados)
- `date_hierarchy` em `created_at` para navegação temporal
- Todos os campos de auditoria como `readonly_fields`

### 🧪 Validação
Fluxo completo testado no shell:
- ✅ Criação de org + user + token + email
- ✅ Slug único gerado corretamente (`empresa-auditoria`)
- ✅ Token válido aceito por `get_valid_token`
- ✅ Consumo grava `used_ip`, `used_ua`, `used_at`
- ✅ Tentativa de reuso bloqueada com `TokenAlreadyUsedError`
- ✅ Teste via navegador: `created_ip` e `created_ua` preenchidos corretamente

### 📦 Migrations aplicadas
- `account/0003_alter_onboardingtoken_options_and_more.py`
  - Novos campos: `created_ip`, `created_ua`, `organization`
  - Alteração em `purpose` (choices expandidos)
  - Índice composto `account_onb_user_id_b91cd1_idx`

### 🎁 Purposes já suportados pelo modelo
- ✅ `ONBOARDING` — ativação inicial de conta (implementado)
- ⏳ `RESET_PASSWORD` — recuperação de senha
- ⏳ `EMAIL_CHANGE` — confirmação de mudança de email
- ⏳ `EMAIL_VERIFICATION` — verificação de email
- ⏳ `INVITATION` — convite de membros para org
- ⏳ `MAGIC_LINK` — login sem senha

### 🔜 Próximos passos
1. **Tela de Setup Password** — consome o token de onboarding e define senha
2. **Fluxo de Reset Password** — reaproveita a infra com novo purpose
3. **Sistema de convites** para adicionar membros a organizações

### 💡 Decisões técnicas
- **Por que UUID no token?** Imprevisibilidade + URL-safe sem encoding extra
- **Por que `data` JSONField?** Flexibilidade para carregar contexto específico por purpose sem criar colunas dedicadas
- **Por que `organization` no token?** Permite auditoria multi-tenant e tokens com contexto organizacional (ex: convite para org específica)
- **Por que exceptions tipadas em vez de retornos booleanos?** Permite que views tratem cada caso com mensagem UX apropriada ao invés de um genérico "token inválido"

---


## 📜 Histórico de Versões

| Versão | Data | Mudanças principais |
|--------|------|---------------------|
| 1.0 | 10/03/2026 | Blueprint inicial |
| 2.0 | 16/04/2026 | Blueprint v2 aprovado — multi-tenant consolidado, ciclo de vida do User, shadow client |
| 2.1 | 17/04/2026 | Refatoração do `account/models.py` concluída: perfis Professional/Client/Assistant como extensões 1:1; OnboardingToken consolidado; soft-delete via archived_at |
| **2.2** | **17/04/2026** | **Resolução de `OperationalError` em migrações (removendo `db.sqlite3` e arquivos de migração); `makemigrations` e `migrate` executados com sucesso para `account` e `core`; `seed_roles` aplicado.** |

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

**Status atual (18/04/2026):**
### ✅ Sprint 1 — Fundação do Onboarding (concluída)
- ✅ `account/models.py` refatorado e validado
- ✅ Migrations aplicadas
- ✅ Seed de Roles
- ✅ `TokenService` com exceptions tipadas e auditoria
- ✅ `OnboardingService.register_organization()`
- ✅ `OnboardingService.setup_password()`
- ✅ Forms: `RegisterForm`, `SetupPasswordForm`
- ✅ Views + URLs (registro e setup de senha)
- ✅ Templates de registro e setup


**Próximo passo imediato:** validar `core/models/tenant.py` e gerar migrations.


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
N10 — Débito técnico: OnboardingToken deveria se chamar UserToken ou AuthToken dado que agora atende múltiplos purposes. Renomear quando houver janela de migration.

| Purpose | TTL | Org? | data necessário | Disparado por |
| --- | --- | --- | --- | --- |
| onboarding | 72h | ✅ Sim | — | Admin cria empresa |
| reset_password | 1h | ❌ Não | — | "Esqueci minha senha" |
| email_change | 24h | ❌ Não | {new_email} | User troca email |
| email_verification | 48h | ❌ Não | — | Auto-registro |
| invitation (futuro) | 7d | ✅ Sim | {role} | Admin convida user |
| magic_link (futuro) | 15min | ❌ Não | — | Login passwordless |

N11 — TTLs de tokens: centralizados em account/constants.py. Para alterar tempo de expiração, editar apenas o dict TOKEN_TTL. Services nunca devem hardcodar timedelta — sempre usar get_token_ttl() ou calculate_expires_at().

N12 — Python version: projeto rodando em 3.9.6 (EOL out/2025). Planejar upgrade para 3.11+ após MVP. Verificar compatibilidade de Django, Celery e dependências antes.

N13 — Auditoria de tokens: model OnboardingToken registra apenas used_ip/used_ua (uso). Avaliar adição de created_ip/created_ua (criação) quando implementar dashboard de segurança / detecção de anomalias. Baixa prioridade.

## 📅 2026-04-18 — Conclusão da Sprint 1: Onboarding Completo

### 🎯 Objetivo
Finalizar o fluxo completo de onboarding de empresa (Etapa 1 + Etapa 2),
com registro público, envio de token e setup de senha com ativação.

### ✅ Entregas

#### 1. `OnboardingService.setup_password()` (account/services/onboarding_service.py)
Método que consome o token de onboarding e ativa user + organização.

**Fluxo (atomic):**
1. Valida token via `TokenService.get_valid_token()`
2. Define senha do user
3. `user.is_active = True`
4. `user.email_verified_at = now()`
5. `organization.is_active = True` (via `OrganizationService.activate_organization()`)
6. Invalida token via `TokenService.invalidate_token()` (com IP e User-Agent)

#### 2. Forms (account/forms.py)

- **`RegisterForm`** — captura email, nome da empresa e CNPJ para Etapa 1
- **`SetupPasswordForm`** — captura e valida senha (com confirmação) para Etapa 2

#### 3. Views + URLs (account/views.py, account/urls.py)

- `RegisterView` — `GET/POST /register/` — exibe form e chama `OnboardingService.register_organization()`
- `SetupPasswordView` — `GET/POST /setup-password/<uuid:token>/` — valida token, exibe form, chama `OnboardingService.setup_password()`
- Tratamento de exceptions tipadas (`TokenExpiredError`, `TokenAlreadyUsedError`, etc.) com mensagens UX apropriadas

#### 4. Templates (account/templates/account/)

- `register.html` — formulário de registro público (layout `base.html`)
- `setup_password.html` — formulário de definição de senha (layout `base.html`)

### 🧪 Validação
- ✅ Registro cria user inativo + org inativa + token + email (console)
- ✅ Link de setup de senha valida e consome token
- ✅ User ativado com senha definida e `email_verified_at` preenchido
- ✅ Organization ativada
- ✅ Token marcado como usado (com auditoria de IP e User-Agent)
- ✅ Tentativa de reuso do token bloqueada com mensagem adequada
- ✅ Token expirado tratado com mensagem adequada

---

### 📌 Status da Sprint 1 — ✅ CONCLUÍDA

| Item | Status |
|------|--------|
| `account/models.py` refatorado | ✅ |
| Migrations aplicadas | ✅ |
| Seed de Roles | ✅ |
| `TokenService` com exceptions tipadas | ✅ |
| `OnboardingService.register_organization()` | ✅ |
| `OnboardingService.setup_password()` | ✅ |
| Forms: `RegisterForm`, `SetupPasswordForm` | ✅ |
| Views + URLs | ✅ |
| Templates de registro e setup | ✅ |

| **2.3** | **18/04/2026** | **Sprint 1 concluída: `setup_password()`, forms, views, URLs e templates de onboarding finalizados. Fluxo completo de registro + ativação funcional.** |

# LiaFit — Notas de Desenvolvimento

## Arquitetura

- **Multi-tenant** via `org_slug` na URL (ex: `/app/{slug}/dashboard/`)
- **Middleware** `TenantMiddleware` injeta `request.context` com org, membership, roles, modules, permissions
- **RBAC** baseado em roles + permissions por módulo
- **Superuser** tem bypass total (não precisa de membership)

---

## Estrutura de Apps

| App | Responsabilidade |
|---|---|
| `account` | User, Organization, OrganizationMember, Role, Module, Permission |
| `core` | Views base (mixins), Dashboard, templates globais |
| `manage` | Seleção/criação de organização (pré-tenant) |

---

## Fluxo de Acesso


---

## Views Base (`core/views/base.py`)

- `BaseAuthMixin` — Login + membership + RBAC (superuser bypassa)
- `ContextMixin` — Filtra queryset por org, injeta tenant/membership nos forms
- `BaseListView` — Lista + filtro + paginação
- `BaseCreateView` — Cria com org automática
- `BaseUpdateView` — Edita com org automática
- `BaseDetailView` — Detalhe filtrado por org
- `BaseDeleteView` — Exclusão filtrada por org

---

## Templates


---

## Middleware

### TenantMiddleware
- Extrai `org_slug` da URL
- Busca `Organization` + `OrganizationMember`
- Monta `request.context` (namedtuple `RequestContext`)
- Rotas sem `org_slug` passam sem contexto

---

## JavaScript

| Arquivo | Função |
|---|---|
| `js/modules/sidebar.js` | Toggle sidebar (desktop colapso + mobile overlay) |
| `js/modules/forms.js` | Helpers de formulário |

---

## Checklist de Progresso

- [x] Models: User, Organization, OrganizationMember, Role, Module, Permission
- [x] Middleware: TenantMiddleware
- [x] Views base: BaseAuthMixin, ContextMixin, CRUD views
- [x] Superuser bypass no BaseAuthMixin e ContextMixin
- [x] Template: base_app.html (layout logado)
- [x] Template: dashboard.html
- [x] JS: sidebar.js
- [ ] Views: manage (select_organization, create_organization)
- [ ] Context processor: tenant_context (org selector no header)
- [ ] Testes automatizados
- [ ] Módulos do SaaS (clients, schedule, financial, etc.)

---

## Último Commit

- **Data**: 2026-04-18
- **Descrição**: Superuser bypass + dashboard + base_app.html
- **Arquivos alterados**:
  - `core/views/base.py` — Superuser bypass no dispatch + queryset
  - `core/views/dashboard.py` — DashboardView
  - `templates/core/dashboard.html` — Template do dashboard
  - `templates/base_app.html` — Layout da área logada
  - `static/js/modules/sidebar.js` — Controle da sidebar



Estrutura de Módulos no Banco: Criamos o modelo de dados para menus dinâmicos (Module e ModuleItem) com suporte a ícones, rotas e controle de exibição.
Correção de Permissões do Superuser:
Alteramos o base.py para que o superuser não seja barrado pela falta de vínculo (membership) com a clínica.
Ajustamos o registry.py para o superuser carregar os módulos do banco ignorando a trava de "módulo comprado/ativado" da organização.
Ativação dos Menus Estáticos: Inserimos o carregamento do menus.py dentro do apps.py (método ready()), fazendo com que os menus fixos do sistema (Global, Tenant e Master) aparecessem com sucesso na tela.
Layout Consolidado: A barra lateral da LiaFit já está exibindo os ícones do Lucide, agrupamentos corretos e os dados do usuário logado (julia@linda.com).
🔍 Diagnóstico Rápido (Observação sobre o seu HTML)
No HTML que você enviou, notei uma coisa importante: Os menus estáticos apareceram, mas os menus do banco de dados (Dashboard, Cadastros) não. Além disso, no meio da tela está escrito: Organização: <strong></strong> (vazio!).

O que isso significa? Você acessou uma URL global (provavelmente a raiz /), onde o sistema ainda não selecionou nenhuma clínica/organização (ou seja, ctx.organization está vazio). Como o registry.py atual só busca no banco se houver uma organização no contexto, os módulos dinâmicos não foram desenhados. Isso está certinho arquiteturalmente, mas amanhã vamos ajustar o fluxo para o usuário entrar na clínica certa.

🚀 O que devemos fazer amanhã (Próximos Passos)
Resolver o Fluxo de Entrada (Tenant Context):
Fazer com que, ao logar, o usuário seja redirecionado para a URL da sua clínica (ex: /org/minha-clinica/dashboard/) para que a tag Organização: seja preenchida e os menus do banco de dados apareçam.
Ou ajustar o registry.py para que o superuser veja os menus do banco mesmo estando fora de uma clínica.
Criar as Views e Rotas que Faltam:
O menu HTML aponta para href="#". Precisamos garantir que as rotas configuradas nos itens do banco e no menus.py (ex: tenant:agenda, master:organizations) existam no urls.py para os links funcionarem e não darem erro 404.
Dar vida aos Cards do Dashboard:
Substituir os — (traços) dos cards de Clientes, Agendamentos Hoje, Faturamento e Serviços Ativos por variáveis de contexto na View (context['total_clientes'], etc) puxando os dados reais do banco.


## Último Commit

- **Data**: 2026-04-20
- **Descrição**: Ordenação de menus estáticos/dinâmicos e hierarquia visual de papéis na sidebar.
- **Arquivos alterados**:
  - `core/config/menus.py` — Adicionado atributo `order=0` (Global) e `order=1000` (Master) para ensanduichar os módulos dinâmicos do tenant.
  - `core/menu/registry.py` — Garantida a ordenação `sort(key=lambda x: getattr(x, 'order', 99))` na lista final de menus.
  - `account/models.py` (ou `core/models.py`) — Adicionada `@property highest_role_name` no `OrganizationMember` para buscar a role ativa de maior `level`.
  - `templates/base_app.html` — Atualizada a div `lia-sidebar__user-role` para exibir "Admin SaaS" (se superuser) ou o cargo de nível mais alto dinamicamente.


| # | Nota | Status |
|---|------|--------|
| N9 | Hierarquia visual de papéis (UI): A sidebar exibe o cargo do usuário baseada na `@property highest_role_name` de `OrganizationMember`, que ordena as Roles ativas pelo maior `level`. | **Implementado** |


- [x] Correção da ordem dos Menus (Global -> Módulos Dinâmicos -> Master)
- [x] Exibição dinâmica do cargo/papel de maior nível na Sidebar (UI)


🚀 **Próximos Passos (Foco Atual):**
1. **Resolver o Fluxo de Entrada (Tenant Context):** Redirecionar usuário logado para `/org/<slug>/dashboard/` para garantir a injeção do tenant e carregamento dos módulos do DB.
2. **Criar as Views e Rotas faltantes:** Trocar os `href="#` pelas rotas reais configuradas no banco e `menus.py`.
3. **Cards do Dashboard:** Popular o contexto da view com dados reais para substituir os marcadores `—`.


Role é por organização.
Unicidade: (organization, name) e (organization, slug).
Seed: criar roles padrão por organização no onboarding da org ou via comando que percorre todas as orgs.
Todas as views herdam BaseAuthMixin com require_tenant=True; RBAC via request.context.permissions.
Pronto. Se quiser, eu já preparo:

link no menu lateral “Papéis (Cargos)”
view de listar permissões de um papel usando seu RolePermissionFilter (se já existir tela).

| N10 | Ativação/desativação de permissões por papel na camada de gestão/RBAC | Pendente |


## Checklist de Progresso

- [x] Models: User, Organization, OrganizationMember, Role, Module, Permission
- [x] Middleware: TenantMiddleware
- [x] Views base: BaseAuthMixin, ContextMixin, CRUD views
- [x] Superuser bypass no BaseAuthMixin e ContextMixin
- [x] Template: base_app.html (layout logado)
- [x] Template: dashboard.html
- [x] JS: sidebar.js
- [x] Fluxo de entrada com redirecionamento para `/org/<slug>/dashboard/`
- [x] Rotas reais dos itens de menu
- [ ] Views: manage (`select_organization`, `create_organization`)
- [ ] Context processor: tenant_context (org selector no header)
- [ ] Cards do dashboard com dados reais
- [ ] Ativar/desativar permissões dos papéis
- [ ] Testes automatizados
- [ ] Módulos do SaaS (clients, schedule, financial, etc.)


🚀 **Próximos Passos (Foco Atual):**
1. **Views de manage:** implementar seleção/criação de organização fora do contexto tenant.
2. **Context processor `tenant_context`:** disponibilizar seletor de organização no header da área logada.
3. **Cards do Dashboard:** popular o contexto da view com dados reais para substituir os marcadores `—`.
4. **Permissões por papel:** permitir ativar ou desativar permissões associadas aos papéis.
5. **Testes automatizados:** cobrir middleware, fluxo tenant, onboarding e RBAC.

## 📌 Arquitetura SaaS / Multi-Tenant

### 1. Modelos (app `account`)
* **`Organization`**: O campo que guarda o nome da empresa se chama **`company_name`** (e não `name`). Todos os templates e queries devem refletir isso.
* **Mapeamento de Tenant**: Identificado pelo campo `slug` na URL (`/app/<org_slug>/...`).

### 2. Middleware (`core.middleware.SaaSContextMiddleware`)
* Intercepta requisições que possuem `org_slug` na URL.
* Valida se a organização está ativa e se o usuário tem uma associação (`OrganizationMember`) ativa.
* **Injeções no `request`**:
  * `request.tenant`: Instância da Organização atual.
  * `request.user_role`: Instância da role (papel/cargo) principal do usuário naquele tenant.
* **Sessão**: Salva o `org_slug` acessado na chave `request.session['last_org_slug']` para lembrar a última clínica acessada pelo usuário.

### 3. Context Processors (`core.context_processors.saas_context`)
* Disponibiliza variáveis globais para os templates (ex: `base_app.html`):
  * `current_organization`: O tenant atual (pego de `request.tenant`).
  * `current_role`: O cargo atual (pego de `request.user_role`).
  * `user_organizations`: Lista de todas as organizações que o usuário faz parte (usado para montar o dropdown de troca de clínica no header).

### 4. Fluxo de Login Dinâmico (Frictionless Login)
* Local: `core.services.post_login.resolve_post_login_redirect`
* **Regras de Redirecionamento Pós-Login:**
  1. **Superusuário**: Vai para o `core:dashboard` ("painel pessoal").
  2. **Usuário sem organização**: Vai para o `core:dashboard`.
  3. **Usuário com 1 organização**: Vai direto para o `tenant:dashboard` da clínica.
  4. **Usuário com múltiplas organizações**: 
     * Tenta direcionar para a última acessada (`last_org_slug` salvo na sessão pelo Middleware).
     * Se não houver histórico, vai para a primeira da lista.
     * Recebe um Toast (mensagem) avisando que pode usar o dropdown do menu para alternar entre os espaços.

### 5. Templates Base (`base_app.html`)
* O Dropdown de seleção de empresas está ativo, iterando sobre `user_organizations`.
* Ao renderizar nomes, sempre utilizar `{{ current_organization.company_name }}` ou `{{ org.company_name }}`.

| N14 | Catálogo de Módulos: fonte da verdade é `core/seeds/modules.py`. 
       Banco é sincronizado via `python manage.py sync_modules` (idempotente). 
       Slugs são readonly no admin. Validação de URLs/permissions via 
       `python manage.py check_modules`. | **Implementado** |
## 📌 Decisões de Arquitetura — Cache RBAC

**Data:** 22/04/2026
**Contexto:** Otimização do `ContextService` (cálculo de permissões por request).

---

### 🎯 Problema identificado

- `ContextService.build_member_context()` executa **5 queries por request**:
  1. Roles do membership
  2. Módulos ativos da organization
  3. Role permissions (filtradas por módulos ativos)
  4. User permissions ALLOW (filtradas por módulos ativos)
  5. User permissions DENY (sem filtro de módulo — DENY sempre vence)
- Precedência: `final = (role_perms ∪ allow_perms) − deny_perms`
- Sem cache → mesmo cálculo repetido em toda request autenticada.
- Benchmark inicial mostrou "speedup 1.3x" que era ilusão (page cache do SO, não cache aplicacional).

---

### ✅ Decisão: Cache adaptativo via env var

**Dev local:** `LocMemCache` (zero setup, funciona igual em Mac e Windows).
**Produção futura:** Upstash Redis (tier grátis, URL no `.env`).
**Seleção automática:** `settings.py` detecta `REDIS_URL` — se existir, usa Redis; senão, LocMem.

**Motivação:**
- Desenvolvimento em 2 OS (Mac + Windows) sem instalar Docker/Redis/Memurai.
- Mesmo código funciona em dev e produção — troca só a env var.
- Django 4.2 já inclui backend `django.core.cache.backends.redis.RedisCache` nativo.

---

### 🛠️ Implementação

#### `settings.py`
```python
import os

REDIS_URL = os.getenv('REDIS_URL', '').strip()

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'TIMEOUT': 300,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'liafit-default',
            'TIMEOUT': 300,
            'OPTIONS': {'MAX_ENTRIES': 10000},
        }
    }

RBAC_CACHE_TTL = 60 * 15       # 15 minutos
RBAC_CACHE_VERSION = 1         # bump para invalidar tudo em deploy
context_service.py
MemberContext e ClientContext como dataclasses.
build_member_context() consulta cache primeiro (HOT path reidrata com objetos Django vivos do request).
COLD path executa 5 queries e popula o cache apenas com dados serializáveis (roles, modules, permissions — sets de strings).
Chave de cache: rbac:ctx:v{version}:u{user_id}:o{organization_id}.
Método ContextService.invalidate(user_id, org_id) para invalidação manual (chamar em signals quando roles/permissions/modules mudarem).
📦 Dependências
Agora (LocMem): nenhuma adicional. Quando migrar pra Redis: adicionar ao requirements.txt:

txt


redis==5.0.8
🎯 Expectativa de performance



Métrica	Valor esperado
❄️ Cold (cache miss)	3–8 ms
🔥 Hot (cache hit)	0.02–0.1 ms
🚀 Speedup	50x – 200x
🔮 Roadmap
 Aplicar cache adaptativo no settings.py
 Refatorar context_service.py com HOT/COLD path
 Rodar benchmark (cold vs hot 100x)
 Adicionar signals de invalidação em mudanças de:
OrganizationMember.roles (M2M change)
UserPermission (save/delete)
RolePermission (save/delete)
OrganizationModule.is_active (save)
 Migrar pra Upstash quando for pra staging/produção
 Considerar bump do RBAC_CACHE_VERSION no CI em cada deploy (invalida tudo automaticamente)
🖥️ Workflow Mac + Windows
Código → GitHub
.env → gerenciador de senhas (1Password/Bitwarden)
.venv → recriado em cada máquina (pip install -r requirements.txt)
db.sqlite3 → local em cada máquina (não sincronizar)
Cache → LocMem local (não sincroniza — é o comportamento desejado em dev)
📚 Stack de referência (22/04/2026)
Python 3.14.0
Django 4.2.30 (LTS — suporte até abril/2026)
SQLite (dev)
Pillow 11.3.0
django-filter 25.1
asgiref 3.11.1
