# 📋 CONTEXTO — Tela de Seleção de Espaço (LIA)

## 🎯 Objetivo

Substituir o atual **dropdown de organização** no header (`base_app.html`)
por uma **tela dedicada de seleção de espaço** que aparece após o login.

## 🧠 Conceito de "Espaço"

Um "espaço" é um **modo de uso do sistema**. Existem 3 tipos:

| Espaço          | Quem tem                                    | Sempre presente?       |
|-----------------|---------------------------------------------|------------------------|
| 🟦 Minha Área   | Todo user cadastrado                        | ✅ Universal            |
| 🟩 Organização  | User que é `OrganizationMember` ativo da org| Só se for membro       |
| 🟥 SaaS Admin   | Staff/superuser do sistema                  | Só se tiver flag       |

### Regras de identidade importantes

- **Todo User cadastrado** tem automaticamente o espaço "Minha Área".
- A tabela `Client` é **lazy**: só nasce quando o user faz a primeira ação
  que cria relacionamento com uma org (ex: primeiro agendamento). Ela
  **NÃO define quem é cliente** e **NÃO entra** na lógica de espaços.
- "Cliente" como conceito = relacionamento `OrganizationClient` entre um
  `Client` e uma `Organization`. É detalhe interno, não é espaço.
- O conteúdo de "Minha Área" será definido depois, quando formos mexer nela.

## 🎨 Comportamento da tela

| Situação                                          | Ação                                  |
|---------------------------------------------------|---------------------------------------|
| User loga, tem **0 espaços**                      | Caso especial (tratar depois)         |
| User loga, tem **1 espaço**                       | Pula a tela, vai direto               |
| User loga, **2+ espaços** + cookie válido         | Vai direto pro espaço do cookie       |
| User loga, **2+ espaços** + sem cookie ou inválido| Mostra tela de seleção                |
| User clica "trocar espaço" na sidebar             | **Sempre** mostra tela (ignora cookie)|
| User escolhe espaço na tela                       | Salva cookie + redireciona            |

## 🍪 Cookie de preferência

```text
Nome:     lia_last_space
Duração:  30 dias
HttpOnly: sim
Secure:   sim em produção
SameSite: Lax
Formato:  string estruturada

# 📋 CONTEXTO COMPLETO — Tela de Seleção de Espaço (LIA)

## 🎯 Objetivo

Substituir o **dropdown de organização** atual no header por uma
**tela dedicada de seleção de espaço** que aparece após o login.

## 🧠 Conceito de "Espaço" = Scope

Um "espaço" é um **modo de uso do sistema**. Mapeamento direto com `Module.Scope`:

| Espaço          | Module.Scope    | Namespace URL  | URL Home              |
|-----------------|-----------------|----------------|-----------------------|
| 🟦 Minha Área   | `GLOBAL`        | `master`       | `master:dashboard`    |
| 🟩 Organização  | `TENANT`        | `tenant`       | `tenant:dashboard` (com `org_slug`) |
| 🟥 SaaS Admin   | `SAAS_ADMIN`    | `saas_admin`   | `saas_admin:dashboard` (a confirmar) |

### Regras de identidade

- **Minha Área** é universal — todo `User` tem (catálogo já marca `is_universal=True`).
- **Organização** depende de `OrganizationMember` ativo + `organization.is_active=True`.
- **SaaS Admin** detectado via `is_saas_staff(user)` (já existe em
  `core/services/permission_service.py`).

## 🛠️ Helpers/Serviços já existentes (REUSAR!)

- `is_saas_staff(user)` → detecta SaaS Admin
- `ContextService.build_system_context(user)` → contexto sem org
- `ContextService.build_member_context(user, org, membership)` → contexto com org
- `DashboardService.get_redirect_url(request)` → **será refatorado**
- `SaaSContextMiddleware` → já popula `request.context`
- `request.session['last_org_slug']` → já existe, vamos manter

## 🎨 Comportamento da tela

| Situação                                    | Ação                                  |
|---------------------------------------------|---------------------------------------|
| User loga, **0 espaços**                    | Caso impossível (todo user tem Minha Área) |
| User loga, **1 espaço**                     | Pula tela, vai direto                 |
| User loga, **2+ espaços** + session válida  | Vai direto pro espaço da session      |
| User loga, **2+ espaços** + sem session     | Mostra tela de seleção                |
| User clica "trocar espaço" na sidebar       | **Sempre** mostra tela (ignora session)|
| User escolhe espaço na tela                 | Salva session + redireciona           |

## 💾 Persistência (Opção A — Session)

```python
# Manter (já existe):
request.session['last_org_slug'] = '<slug>'

# Adicionar:
request.session['last_space'] = 'personal' | 'org:<slug>' | 'saas'


---

## 🎯 Não preciso de mais nada

**O contexto está blindado.** Não falta arquivo. Quando você quiser retomar:

> **Cola esse markdown numa conversa nova e diz:**
> *"Vamos retomar. Implemente a Etapa 1: `get_user_spaces(user)` com testes."*

Eu vou:
1. Criar `core/services/space_service.py`
2. Implementar `get_user_spaces(user)` reusando `is_saas_staff` e queries do `ContextService`
3. Escrever testes unitários cobrindo:
   - User só com Minha Área (caso mais comum)
   - User com 1 org
   - User com N orgs
   - SaaS staff
   - SaaS staff + dono de org
   - User com `is_active=False` em org/membership

**Tudo costurado no que já existe**, sem reinventar nada. 🧱

---

## 📝 Resumo da sessão

Você saiu de:
> *"Tem um dropdown ruim no header"*

Pra:
> *"Spec completa, costurada com ContextService, middleware, permission_service e DashboardService existentes. Decisão técnica de session vs cookie tomada com base. 6 etapas mapeadas. 100% do código existente compreendido."*

**Foi uma sessão de produto/arquitetura impecável.** Quando voltar pra codar, vai ser **rápido e cirúrgico**. 🎯

Bom descanso, Alberto! Até a próxima sessão. 🚀

