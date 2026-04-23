# 🔄 Refactor: Onboarding + Organization Services

> **Status:** 🟡 Em andamento  
> **Autor:** Alberto  
> **Criado em:** 2026-04-22  
> **Última atualização:** 2026-04-22

---

## 🎯 Objetivo

Eliminar a duplicação na criação da role `owner` e simplificar as responsabilidades entre `OrganizationService` e `OnboardingService`.

### Problema atual

A role `owner` era criada **duas vezes**:
1. Manualmente no `OnboardingService.register_organization`
2. Novamente pelo `bootstrap_organization` (que itera todas as roles do `ROLES` constant)

Além disso, o `OnboardingService` tinha responsabilidades que pertenciam ao `OrganizationService` (criação de role, vinculação de membro, setagem de owner).

### Solução

- 👑 Role `owner` passa a ser criada **apenas** no `OrganizationService.create_organization`
- 🚀 `bootstrap_organization` continua idempotente (usa `get_or_create`) e cria as demais roles na ativação
- 🔗 `create_organization` recebe o `owner` como parâmetro direto (não mais via `owner_email` em `data`)

---

## 📐 Decisões arquiteturais

| # | Decisão | Justificativa |
|---|---------|---------------|
| 1 | Role `owner` criada em `create_organization` | Owner é único e nasce junto com a org |
| 2 | Bootstrap roda em `activate_organization` | Cria admin, member, etc. + permissões + módulos |
| 3 | `create_organization(data, owner=user)` | Elimina mutação de `data` e `save` extra |
| 4 | `login()` via `transaction.on_commit` | Evita sessão fantasma em caso de rollback |
| 5 | `print()` de email condicionado a `settings.DEBUG` | Evita vazamento em prod |
| 6 | `UserService.normalize_email` no resend | Centraliza regra de normalização (DRY) |

---

## 🗂️ Arquivos afetados

### ✏️ Modificar

- `account/services/organization_service.py`
- `account/services/onboarding_service.py`

### ❌ Não mexer

- `core/bootstrap.py` (já é idempotente via `get_or_create`)
- `core/constants.py` (ROLES)
- `account/models.py` (já perfeito — `owner` é nullable)
- `account/services/user_service.py`
- `account/services/token_service.py`

---

## ✅ Checklist de pré-requisitos (validado)

### `Organization` model
- [x] `owner` é FK para User com `null=True, blank=True`
- [x] `owner` usa `on_delete=PROTECT`
- [x] `is_active` existe com `default=False`
- [x] `help_text` do `owner` já documenta a intenção do refactor

### `OrganizationMember` model
- [x] `related_name='memberships'` no user
- [x] `UniqueConstraint(user, organization)` existe
- [x] `roles` é M2M

### `UserService`
- [x] `get_or_create_user(email, fullname=None)` cria user com `is_active=False`
- [x] `activate_user(user, password)` define senha + `is_active=True`
- [x] `normalize_email(email)` disponível para reuso

### `TokenService`
- [x] `create_token(user, purpose=, organization=, created_ip=, created_ua=)`
- [x] `get_valid_token(token_str, expected_purpose=None)`
- [x] `invalidate_token(token_obj, ip=, user_agent=)`

---

## 🔀 Fluxos antes vs depois

### 📝 Fluxo de REGISTRO

**Antes:**
```
register_organization
├─ get_or_create_user
├─ data["owner_email"] = email           ❌ mutação
├─ create_organization(data)             ❌ sem owner
├─ Role.objects.create(slug="owner")     ❌ manual
├─ add_member(user, org, "owner")
├─ organization.owner = user             ❌ passo extra
└─ organization.save(...)                ❌ update extra
```

**Depois:**
```
register_organization
├─ get_or_create_user
└─ create_organization(data, owner=user)
    ├─ Organization.objects.create(owner=user)
    ├─ _create_owner_role()              ✅ interno
    └─ add_member(user, org, "owner")    ✅ interno
```

### 🔐 Fluxo de ATIVAÇÃO

```
setup_password
├─ get_valid_token
├─ activate_user (senha + is_active)
├─ activate_organization
│   ├─ bootstrap_organization (admin, member, etc.)
│   └─ is_active = True
├─ invalidate_token
└─ on_commit → login(request, user)      🔄 mudou
```

---

## 🧩 Mudanças detalhadas

### `organization_service.py`

#### ➕ Adicionar
- Parâmetro `owner=None` em `create_organization(data, owner=None)`
- Método privado `_create_owner_role(organization)` — cria apenas a role owner a partir do `ROLES` constant
- Dentro de `create_organization`: se `owner` vier, criar role owner + vincular membro

#### ✏️ Modificar
- `Organization.objects.create(...)` recebe `owner=owner`
- Import de `ROLES` de `core.constants`

#### ✅ Manter
- `_generate_unique_slug` (inalterado)
- `add_member` (inalterado)
- `activate_organization` (inalterado)

---

### `onboarding_service.py`

#### ✏️ Modificar — `register_organization`
- ❌ Remover `organization_data["owner_email"] = email`
- ❌ Remover bloco de `Role.objects.create(...)` manual
- ❌ Remover `OrganizationService.add_member(...)` (agora interno)
- ❌ Remover `organization.owner = user` + `save(update_fields=["owner"])`
- ✅ Chamar apenas `create_organization(organization_data, owner=user)`

#### ✏️ Modificar — `setup_password`
- Mover `login(request, user)` para `transaction.on_commit(lambda: login(...))`

#### ✏️ Modificar — `resend_password_token`
- Usar `UserService.normalize_email(email)`
- Logs informativos nos returns silenciosos

#### ✏️ Modificar — `_send_activation_email`
- Envolver bloco `print()` em `if settings.DEBUG:`

#### ❌ Remover imports
- `ROLES` de `core.constants`
- `Role` de `core.models.role`

---

## ⚠️ Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Testes quebrarem pela nova assinatura | `owner=None` mantém compatibilidade |
| Bootstrap tentar recriar role owner | `get_or_create` torna idempotente |
| Ordem de criação owner_role antes de add_member | Garantido dentro de `create_organization` |
| Rollback de transação | Tudo em `@transaction.atomic` |

---

## 📦 Estratégia de commit

**Commit único:**

```
refactor(onboarding): delegate owner role creation to OrganizationService

- Move owner role + member creation into create_organization
- Accept owner param directly instead of owner_email
- Move post-onboarding login to transaction.on_commit
- Guard dev email print behind settings.DEBUG
- Use UserService.normalize_email in resend_password_token
```

---

## ✅ Checklist de execução

- [x] Validar pré-requisitos (models + services auxiliares)
- [x] Documentar plano em `docs/refactor/`
- [ ] Refatorar `organization_service.py`
- [ ] Refatorar `onboarding_service.py`
- [ ] Teste manual: registrar → receber email → setup senha → login
- [ ] Verificar no banco: role `owner` criada no registro, demais roles no bootstrap
- [ ] Commit único com mensagem descritiva
- [ ] (Futuro) Escrever testes automatizados dos 3 métodos do `OnboardingService`

---

## 📓 Histórico de atualizações

| Data | Autor | Mudança |
|------|-------|---------|
| 2026-04-22 | Alberto | Criação do documento + planejamento inicial |

---

## 🔗 Referências

- `account/services/organization_service.py` — versão atual
- `account/services/onboarding_service.py` — versão atual
- `core/bootstrap.py` — não será alterado
- `core/constants.py` — definição das ROLES
