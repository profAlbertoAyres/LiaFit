# BUG #1 — App `saas_admin` referenciado mas não instalado

## 🎯 Contexto
Projeto **Lia Linda** (Django 4.2, SaaS multi-tenant para personal trainers).

## 📍 Localização
- `config/settings.py` — lista `INSTALLED_APPS`
- `config/urls.py` — `urlpatterns`
- `core/constants/catalog.py` — referência a rota `saas_admin:organization_list`

## 🐛 Descrição do bug
O arquivo `config/urls.py` inclui o app `saas_admin`:

```python
path('admin-saas/', include(('saas_admin.urls', 'saas_admin'), namespace='saas_admin')),
```

E o catálogo (`core/constants/catalog.py`) declara um módulo com rotas no namespace `saas_admin`:

```python
{
    "slug": ModuleSlug.SAAS_ADMIN,
    "scope": "superuser",
    "items": [
        {
            "slug": ItemSlug.ORGANIZATIONS,
            "route": "saas_admin:organization_list",
            ...
        },
    ],
},
```

Porém, o app `'saas_admin'` **NÃO está declarado** em `INSTALLED_APPS` no `settings.py`. A lista atual contém apenas:

```python
INSTALLED_APPS = [
    # django defaults...
    'django_filters',
    'core',
    'account',
    'website',
    'financial',
    'shared',
    'scheduling',
    'workout',
    # 'saas_admin' ← FALTANDO
]
```

## 💥 Impactos possíveis
1. **`ImportError`/`ModuleNotFoundError`** ao subir o servidor (se o módulo não existir no projeto)
2. **`ImproperlyConfigured`** se houver `app_label` referenciado em models do app
3. Templates de `saas_admin` não são descobertos por `APP_DIRS`
4. Migrations do app não são aplicadas
5. O comando `python manage.py check_catalog` vai reportar a rota `saas_admin:organization_list` como `NoReverseMatch`

## 🔍 Investigação prévia necessária
- O diretório `saas_admin/` realmente existe no projeto?
- Se existe: tem `apps.py`, `urls.py`, `models.py`, `views.py`?
- Se não existe: o catálogo está adiantado em relação à implementação?

## 🛑 Fluxo obrigatório
1. **Análise:** verificar existência do app, suas dependências e o estado atual
2. **Plano de correção em conjunto:** decidir se é caso de criar o app do zero, instalar um já existente, ou remover a referência prematura no catálogo
3. **Aprovação** do plano
4. **Só então** codificar



# BUG #2 — `OnboardingService.resend_password_token()` não existe

## 🎯 Contexto
Projeto **Lia Linda** — sistema de onboarding com tokens (`OnboardingToken`) para múltiplos propósitos: ativação de conta, reset de senha, mudança de email, magic link, convite, etc.

## 📍 Localização
- `account/views/organization_view.py` — método `post()` ou similar
- `account/services/onboarding_service.py` — classe `OnboardingService`

## 🐛 Descrição do bug
Em `organization_view.py`, há uma chamada para um método inexistente:

```python
OnboardingService.resend_password_token(user, ...)
```

Porém, ao examinar `account/services/onboarding_service.py`, **não existe** método chamado `resend_password_token`. Os métodos reais relacionados a reenvio são:

- `OnboardingService.resend_activation_token(user, organization)` — reenvia token de ativação
- `OnboardingService.send_password_reset(user, ...)` — envia novo token de reset

A intenção provável é **reenviar o token de reset de senha**, mas o nome do método está errado (resquício de refatoração ou typo).

## 💥 Impactos possíveis
1. **`AttributeError: type object 'OnboardingService' has no attribute 'resend_password_token'`** quando o usuário aciona a ação correspondente
2. Funcionalidade de "reenviar email de redefinição de senha" totalmente quebrada
3. Falha silenciosa em logs se houver `try/except Exception` engolindo o erro

## 🔍 Investigação prévia necessária
- Qual é a intenção real? Reenviar token de reset (RESET_PASSWORD) ou de ativação (ONBOARDING)?
- A view chama esse método em qual cenário (admin reenvia? usuário pede de novo?)
- Existe algum `OnboardingToken.Purpose` específico que deveria ser usado?
- O `OnboardingService` tem método `send_password_reset()` que poderia ser reutilizado?

## 🛑 Fluxo obrigatório
1. **Análise:** mapear o caso de uso real e ver qual método existente atende (ou se precisa criar um novo)
2. **Plano de correção em conjunto:** decidir entre (a) renomear chamada para método existente, (b) criar `resend_password_token` no service, (c) refatorar para um único `resend_token(purpose)` genérico
3. **Aprovação** do plano
4. **Só então** codificar

# BUG #3 — Typo: `settings.changer_member` em permission_required

## 🎯 Contexto
Projeto **Lia Linda** — RBAC com codenames de permissão no formato `<module_slug>.<action>_<item_slug>`. Exemplos válidos: `settings.view_member`, `settings.add_member`, `settings.change_member`, `settings.delete_member`.

O catálogo declarativo (`core/constants/catalog.py`) é a fonte da verdade. Para o item `MEMBER` com actions `CRUD + INVITE`, são geradas as permissões:
- `settings.view_member`
- `settings.add_member`
- `settings.change_member`  ← **a correta**
- `settings.delete_member`
- `settings.invite_member`

## 📍 Localização
- `account/views/member_views.py` — classe `MemberUpdateView` (ou similar)

## 🐛 Descrição do bug
Há erro ortográfico na permissão exigida:

```python
class MemberUpdateView(BaseUpdateView):
    permission_required = "settings.changer_member"  # ❌ "changer" → deveria ser "change"
```

O codename `settings.changer_member` **não existe** no banco (não foi gerado pelo bootstrap, pois o catálogo só define `CRUD = [view, add, change, delete]`).

## 💥 Impactos possíveis
1. **Nenhum usuário consegue editar membros**, exceto:
   - `is_superuser` (bypassa via `BaseAuthMixin`)
   - SaaS staff (bypassa)
   - Owner do tenant (bypassa)
2. Para owners/admins normais com `settings.change_member` legítima → **acesso negado** com mensagem "Você não tem permissão para acessar esta funcionalidade"
3. Bug silencioso: nenhum erro no servidor, só comportamento errado no front

## 🔍 Investigação prévia necessária
- Existem outros lugares com `changer_*` em vez de `change_*`? (grep no projeto inteiro)
- Há testes que cobrem fluxo de edição de membro? (provavelmente não, senão o bug seria pego)

## 🛑 Fluxo obrigatório
1. **Análise:** confirmar que é caso isolado (ou identificar outros typos similares)
2. **Plano de correção em conjunto:** simples find/replace, mas considerar adicionar validação no startup (ex: management command que verifica se todos `permission_required` declarados nas views existem no catálogo)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #4 — URL `role_permissions_update` aponta para view errada (RoleCreateView)

## 🎯 Contexto
Projeto **Lia Linda** — gestão de roles tenant (`Role`) e suas permissões (`RolePermission`).

A view `RoleDetailView` em `core/views/role_view.py` já implementa o método `post()` que processa atualização de permissões via formulário de checkboxes:

```python
class RoleDetailView(BaseDetailView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        selected_permission_ids = request.POST.getlist('permissions')
        membership = self.get_membership()
        RoleService.process_role_permissions_update(
            request=self.request,
            role=self.object,
            membership=membership,
            selected_permission_ids=selected_permission_ids
        )
        return redirect('tenant:role_detail', ...)
```

## 📍 Localização
- `core/urls/tenant.py` — declaração de URLs do escopo tenant

## 🐛 Descrição do bug
A URL para atualizar permissões de um role aponta para `RoleCreateView` (provável copy-paste):

```python
path(
    'roles/<int:pk>/permissions/',
    RoleCreateView.as_view(),                    # ❌ ERRADO
    name='role_permissions_update'
),
```

## 💥 Impactos possíveis
1. Submeter o formulário de permissões cai em `RoleCreateView`, que tenta **criar um novo role** em vez de atualizar permissões
2. Pode gerar erros de form (RoleCreateView espera `RoleForm`, não recebe os campos)
3. Cria entidades indesejadas se o form casualmente validar
4. Tela em branco / 500 / criação espúria de roles "fantasma"

## 🔍 Investigação prévia necessária
- Existe uma view dedicada (`RolePermissionsUpdateView`?) ou o fluxo correto é apontar para `RoleDetailView` (que já trata o POST)?
- Como o template envia o form? Para `tenant:role_detail` ou para `tenant:role_permissions_update`?
- Há outras URLs com copy-paste similar?

## 🛑 Fluxo obrigatório
1. **Análise:** verificar template `core/role/detail.html` para descobrir para qual URL ele faz POST
2. **Plano de correção em conjunto:** opções:
   - (a) trocar para `RoleDetailView.as_view()` (consolidar GET+POST na mesma view)
   - (b) criar uma view `RolePermissionsUpdateView` dedicada
   - (c) alinhar o template para postar em `tenant:role_detail` (e remover essa URL redundante)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #5 — DashboardView combina TemplateView + ContextMixin (potencial AttributeError)

## 🎯 Contexto
Projeto **Lia Linda** — `ContextMixin` (em `core/views/base_view.py`) é um mixin pensado para ser combinado com `ListView`, `CreateView`, `UpdateView`, etc., que possuem `get_queryset()`. Ele sobrescreve `get_queryset()` chamando `super().get_queryset()` e aplicando filtros multi-tenant:

```python
class ContextMixin:
    def get_queryset(self):
        queryset = super().get_queryset()  # ← assume que existe na classe pai
        if getattr(self, 'require_tenant', True) is False:
            return queryset
        ...
```

## 📍 Localização
- `core/views/dashboard_view.py`

## 🐛 Descrição do bug
`DashboardView` herda de `TemplateView`, que **não tem** `get_queryset()`:

```python
class DashboardView(ContextMixin, BaseAuthMixin, TemplateView):
    template_name = 'core/dashboard/dashboard.html'
    require_tenant = False
    
    def dispatch(self, request, *args, **kwargs):
        redirect_url = DashboardService.get_redirect_url(request)
        if redirect_url:
            return redirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)
```

Se algum código (template tag, signal, mixin futuro, ou refatoração) fizer com que `get_queryset()` seja chamado, dispara:

```
AttributeError: 'super' object has no attribute 'get_queryset'
```

## 💥 Impactos possíveis
1. **Bomba-relógio:** atualmente não dispara porque `dispatch` redireciona ou nada chama `get_queryset()`
2. Qualquer adição futura no `ContextMixin` que assuma `get_queryset` quebra essa view
3. Aumenta acoplamento e dificulta manutenção
4. Quebra o princípio da separação de responsabilidades — `ContextMixin` só deveria ser usado em CBVs de modelo

## 🔍 Investigação prévia necessária
- `ContextMixin` é usado em outras `TemplateView`s no projeto? (grep)
- Existe um padrão alternativo para "view sem queryset que ainda precisa de tenant context"?
- O método `get_form_kwargs` do `ContextMixin` também é problemático em TemplateView?

## 🛑 Fluxo obrigatório
1. **Análise:** mapear quais métodos do `ContextMixin` realmente são usados pelo `DashboardView` (provavelmente só `get_tenant`/`get_membership`)
2. **Plano de correção em conjunto:** opções:
   - (a) criar um `ContextTemplateMixin` mais leve sem `get_queryset`/`get_form_kwargs`
   - (b) adicionar `hasattr(super(), 'get_queryset')` guard no `ContextMixin`
   - (c) split: `TenantContextMixin` (só helpers) + `TenantQuerysetMixin` (filtros)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #6 — `success_url` em reverse_lazy sem namespace

## 🎯 Contexto
Projeto **Lia Linda** — URLs organizadas em **namespaces**:
- `master:` — admin do catálogo (sem org_slug)
- `tenant:` — escopo da organização (com org_slug)
- `auth:` — autenticação
- `saas_admin:` — admin LiaFit
- `website:` — site público

Toda referência via `reverse()` ou `reverse_lazy()` precisa do prefixo de namespace.

## 📍 Localização
- `core/views/master_view.py` — `ModuleCreateView`, `PermissionCreateView`, `RoleCreateView`
- `core/views/tenant_view.py` — `RolePermissionCreateView`, `UserPermissionCreateView`

## 🐛 Descrição do bug
Diversas views declaram `success_url` sem namespace:

```python
# core/views/master_view.py
class ModuleCreateView(BaseCreateView):
    success_url = reverse_lazy('module_list')  # ❌ falta 'master:'

class PermissionCreateView(BaseCreateView):
    success_url = reverse_lazy('permission_list')  # ❌ falta 'master:'

# core/views/tenant_view.py
class RolePermissionCreateView(BaseCreateView):
    success_url = reverse_lazy('tenant_role_permission_list')  # ❌ nome inexistente
```

## 💥 Impactos possíveis
1. **`NoReverseMatch`** ao salvar formulário com sucesso → 500 Internal Server Error
2. Formulário grava no banco mas tela quebra → usuário acha que não salvou e tenta de novo (duplicata)
3. `tenant_role_permission_list` provavelmente nem existe como nome — precisa verificar

## 🔍 Investigação prévia necessária
- Listar todos os `name=` declarados em `core/urls/master.py` e `core/urls/tenant.py`
- Identificar qual nome correto cada `success_url` deveria apontar
- Verificar se há outras views com o mesmo problema (grep `reverse_lazy(['"][a-z_]+['"]` sem `:`)

## 🛑 Fluxo obrigatório
1. **Análise:** mapear cada `success_url` errado para o nome correto
2. **Plano de correção em conjunto:** decidir se vale criar lint customizado / teste para detectar reverse sem namespace; quais nomes usar (ex: `master:module_list` vs `master:modules`)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #7 — Typo no nome do arquivo: `deshboard_service.py`

## 🎯 Contexto
Projeto **Lia Linda** — convenção de nomenclatura: arquivos em snake_case, em inglês, refletindo o conteúdo.

## 📍 Localização
- `core/services/deshboard_service.py` (deveria ser `dashboard_service.py`)
- Imports em `core/views/dashboard_view.py`:
  ```python
  from core.services.deshboard_service import DashboardService
  ```

## 🐛 Descrição do bug
O arquivo se chama **`deshboard_service.py`** (com "e" no lugar de "a"). O comentário interno do arquivo também está errado:

```python
# core/services/dashboard_view.py   ← arquivo é service, não view
```

## 💥 Impactos possíveis
1. **Zero impacto funcional** — Python não liga para o nome
2. Confunde durante manutenção / busca por arquivo
3. Quebra IDE search por "dashboard_service"
4. Inconsistência com o padrão `dashboard_view.py` (que está correto)

## 🔍 Investigação prévia necessária
- Quantos lugares importam `deshboard_service`? (grep)
- Há referências em strings (ex: `LOGGING`, `INSTALLED_APPS`)?
- Há migrations ou Celery tasks referenciando?

## 🛑 Fluxo obrigatório
1. **Análise:** listar todos os pontos de import
2. **Plano de correção em conjunto:** decidir se renomeia agora (e atualiza imports) ou mantém + alias temporário; considerar git rename para preservar histórico
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #8 — Comentário de cabeçalho de arquivo errado

## 🎯 Contexto
Projeto **Lia Linda** — diversos arquivos têm comentários de cabeçalho que indicam o caminho do arquivo (boa prática de orientação).

## 📍 Localização
- `core/services/deshboard_service.py` linha 1:
  ```python
  # core/services/dashboard_view.py   ← arquivo é service, não view, e o nome está com typo
  ```
- Possivelmente outros arquivos com cabeçalho desatualizado

## 🐛 Descrição do bug
Comentário no topo do arquivo aponta para um caminho que **não corresponde** ao arquivo real. Indica que houve refatoração / mudança de localização sem atualizar o cabeçalho.

## 💥 Impactos possíveis
1. **Zero impacto funcional**
2. Confunde leitor durante code review
3. Em ferramentas que extraem documentação automática, o caminho fica errado
4. Pode esconder bug #7 (typo no nome do arquivo)

## 🔍 Investigação prévia necessária
- Existe convenção formal sobre cabeçalho? (todos arquivos devem ter? só alguns?)
- Há outros arquivos com cabeçalho desatualizado? (grep `^# core/.*\.py`)

## 🛑 Fluxo obrigatório
1. **Análise:** decidir se mantém a convenção (atualizar todos) ou abandona (remover todos)
2. **Plano de correção em conjunto:** se manter, considerar pre-commit hook ou linter customizado pra validar
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #9 — `LOGIN_REDIRECT_URL` hard-coded como string

## 🎯 Contexto
Projeto **Lia Linda** — Django 4.2, settings em `config/settings.py`. URL pública `/dashboard/` é declarada em `config/urls.py` com `name='dashboard'` (sem namespace, no nível raiz).

## 📍 Localização
- `config/settings.py`:
  ```python
  LOGIN_URL = 'auth:login'
  LOGIN_REDIRECT_URL = '/dashboard/'  # ❌ hard-coded
  LOGOUT_REDIRECT_URL = 'website:index'
  ```
- `config/urls.py`:
  ```python
  path('dashboard/', DashboardView.as_view(), name='dashboard'),
  ```

## 🐛 Descrição do bug
`LOGIN_REDIRECT_URL` está como **string crua** `/dashboard/`, em vez de usar o **nome da URL** (Django aceita ambos, mas o nome é desacoplado).

`LOGIN_URL` e `LOGOUT_REDIRECT_URL` usam o nome da URL (correto). Inconsistência interna.

## 💥 Impactos possíveis
1. Se a URL `/dashboard/` for renomeada (ex: `/painel/`), login passa a redirecionar para 404
2. Quebra silenciosa: settings continua "válido", mas comportamento errado
3. Dificulta migração para outra URL (precisa lembrar desse ponto)

## 🔍 Investigação prévia necessária
- Há outros pontos com URL hard-coded em settings ou middleware?
- `DashboardView` no `urls.py` raiz é mantida ou deveria ser unificada com `tenant:dashboard`?

## 🛑 Fluxo obrigatório
1. **Análise:** decidir convenção (todas string OU todas nome)
2. **Plano de correção em conjunto:** trocar para `LOGIN_REDIRECT_URL = 'dashboard'`; verificar impacto em testes
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #10 — Configuração de LOGGING praticamente vazia

## 🎯 Contexto
Projeto **Lia Linda** — Django 4.2, em produção espera-se rodar atrás de um servidor WSGI (gunicorn/uvicorn) com logs centralizados.

## 📍 Localização
- `config/settings.py`:
  ```python
  LOGGING = {
      'version': 1,
      'disable_existing_loggers': False,
  }
  ```

## 🐛 Descrição do bug
A configuração de logging só tem o esqueleto mínimo: nenhum **handler**, **formatter** ou **logger** customizado declarado.

Embora os arquivos de service usem `logger = logging.getLogger(__name__)` (ex: `core/services/bootstrap/catalog.py`), as mensagens caem no logger root do Django, que em produção pode não estar configurado para escrever em arquivo / agregador.

## 💥 Impactos possíveis
1. **Em produção:** logs de `logger.warning(...)`, `logger.error(...)` podem se perder
2. Sem rastreabilidade em incidentes
3. `print()` espalhados (vi vários em `bootstrap/catalog.py` com `verbose=True`) misturam com logs estruturados
4. Sem rotação de logs → arquivos podem crescer indefinidamente

## 🔍 Investigação prévia necessária
- Onde o app vai rodar? (Render, Heroku, AWS, VPS?) → cada um tem coleta de stdout/stderr
- Há intenção de usar Sentry / Datadog / outro agregador?
- Quais loggers são usados no código? (grep `getLogger`)

## 🛑 Fluxo obrigatório
1. **Análise:** mapear loggers existentes e definir níveis
2. **Plano de correção em conjunto:** definir estrutura mínima:
   - handler `console` (stream handler)
   - handler `file` opcional (com rotação)
   - formatter padrão (JSON ou texto)
   - loggers para `django`, `core`, `account`
   - integração futura com Sentry?
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #11 — Inconsistência entre actions `INVITE` e `ADD` para Member

## 🎯 Contexto
Projeto **Lia Linda** — sistema RBAC com `ActionSlug` (enum em `core/constants/permissions.py`):

```python
class ActionSlug(models.TextChoices):
    VIEW   = "view"
    ADD    = "add"
    CHANGE = "change"
    DELETE = "delete"
    INVITE = "invite"  # 🆕 ação especial
```

O catálogo (`core/constants/catalog.py`) declara para o item `MEMBER`:
```python
{
    "slug": ItemSlug.MEMBER,
    "actions": CRUD + [ActionSlug.INVITE],  # gera 5 permissions
},
```

Isso gera no banco:
- `settings.view_member`
- `settings.add_member`
- `settings.change_member`
- `settings.delete_member`
- `settings.invite_member`  ← ação dedicada para "convidar via email"

## 📍 Localização
- `account/views/member_views.py` — `MemberCreateView`

## 🐛 Descrição do bug
A `MemberCreateView` (que cria um novo membro via convite por email) exige a permissão **`settings.add_member`**, não `settings.invite_member`:

```python
class MemberCreateView(BaseCreateView):
    permission_required = "settings.add_member"  # ❓ deveria ser invite_member?
```

A intenção do catálogo era separar:
- **`add_member`** — adicionar manualmente (admin com poder total)
- **`invite_member`** — enviar convite por email (gestor sem poder de criar direto)

Mas a implementação trata os dois como `add`. Resultado: **`settings.invite_member` existe no banco mas nunca é checada**.

Confirmação do gap: o role `manager` em `core/constants/roles.py` recebe explicitamente:
```python
{
    "item": (ModuleSlug.SETTINGS, ItemSlug.MEMBER),
    "actions": [ActionSlug.INVITE, ActionSlug.CHANGE],  # invite, NÃO add
},
```

Ou seja: o `manager` tem `invite_member` mas **não tem** `add_member` → vai cair em "acesso negado" ao tentar convidar membro.

## 💥 Impactos possíveis
1. **Role `manager` não consegue convidar membros**, embora o catálogo declare que ele deveria
2. Permissão `invite_member` "fantasma" no banco (nunca usada)
3. Ambiguidade de domínio: "convidar" e "adicionar" são iguais ou diferentes?

## 🔍 Investigação prévia necessária
- A view de criação de membro **realmente** envia convite por email, ou cria direto?
- Existe view separada de "convite"? (ex: `MemberInviteView`)
- O que o owner/admin faz: convite ou criação direta? E o manager?

## 🛑 Fluxo obrigatório
1. **Análise:** entender modelo de domínio (convite ≠ criação?) e decidir nomenclatura
2. **Plano de correção em conjunto:** opções:
   - (a) trocar `permission_required` para `settings.invite_member`
   - (b) usar `permission_required_any = ('settings.add_member', 'settings.invite_member')`
   - (c) remover ação `invite` do catálogo (se for sinônimo de `add`)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #12 — `RoleListView` declarada em DOIS namespaces com classes diferentes

## 🎯 Contexto
Projeto **Lia Linda** — separação de scope em namespaces:
- `master:` — admin do catálogo (sem tenant)
- `tenant:` — escopo da organização

## 📍 Localização
- `core/views/master_view.py`:
  ```python
  class RoleListView(BaseListView):
      model = Role
      template_name = 'core/role_list.html'
      require_tenant = False
  ```
- `core/views/role_view.py`:
  ```python
  class RoleListView(BaseListView):
      model = Role
      template_name = 'core/role/list.html'
      permission_required = 'settings.view_role'
      filterset_class = RoleFilter
  ```
- `core/urls/master.py` → `master:role_list` aponta para a primeira
- `core/urls/tenant.py` → `tenant:role_list` aponta para a segunda

## 🐛 Descrição do bug
Existem **duas classes com o mesmo nome `RoleListView`** em arquivos diferentes do mesmo app, com comportamentos distintos:

| Aspecto | master_view.py | role_view.py |
|---------|----------------|---------------|
| `require_tenant` | False | True |
| `permission_required` | None | `settings.view_role` |
| `filterset_class` | None | `RoleFilter` |
| Template | `core/role_list.html` | `core/role/list.html` |

Imports ambíguos exigem cuidado:
```python
from core.views.master_view import RoleListView  # admin
from core.views.role_view import RoleListView    # tenant
# Não pode importar ambas no mesmo módulo sem alias
```

## 💥 Impactos possíveis
1. Confusão durante leitura/manutenção
2. Risco de import errado se IDE auto-sugerir
3. Em refatorações futuras, mudanças em uma podem ser confundidas com a outra
4. Dificuldade de procurar no projeto ("qual `RoleListView`?")

## 🔍 Investigação prévia necessária
- Os comportamentos realmente justificam classes separadas, ou poderiam ser uma só com flags?
- Há outras classes com nomes duplicados? (`RoleCreateView` também aparece nos dois)

## 🛑 Fluxo obrigatório
1. **Análise:** comparar as duas classes e ver overlap
2. **Plano de correção em conjunto:** opções:
   - (a) renomear: `MasterRoleListView` + `TenantRoleListView`
   - (b) unificar com flag: `RoleListView(require_tenant=True/False)`
   - (c) manter mas usar aliases nos imports (`as MasterRoleListView`)
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #13 — `ClientProfessional` pode não estar exportado em `account/models/__init__.py`

## 🎯 Contexto
Projeto **Lia Linda** — convenção de exports: `account/models/__init__.py` re-exporta classes dos arquivos individuais (`user.py`, `organization.py`, `member.py`, `client.py`, etc.) para permitir import limpo:

```python
from account.models import User, Organization, OrganizationMember, OrganizationClient
```

## 📍 Localização
- `account/services/client_service.py`:
  ```python
  from account.models import Client, ClientProfessional  # ⚠️ ClientProfessional?
  ```
- `account/models/__init__.py` — listagem de exports
- `account/models/client.py` — definição de `Client` e possivelmente `ClientProfessional`

## 🐛 Descrição do bug
O service `client_service.py` importa `ClientProfessional` de `account.models`, mas essa classe **não foi observada** explicitamente no `__init__.py` que mapeei. Possíveis cenários:
1. A classe existe em `account/models/client.py` mas **não está re-exportada** no `__init__.py`
2. A classe existe em outro arquivo e foi esquecida
3. A classe nunca foi criada (resquício de planejamento)

## 💥 Impactos possíveis
1. Se cenário 1: `ImportError: cannot import name 'ClientProfessional' from 'account.models'`
2. Service quebra em runtime ao primeiro uso
3. Onboarding / vínculo de cliente com profissional fica inviável
4. Gap entre código existente e domínio modelado

## 🔍 Investigação prévia necessária
- Confirmar existência de `ClientProfessional` em `account/models/client.py` (ou outro arquivo)
- Listar campos/relações do modelo
- Verificar se há migrations que criam essa tabela
- Ver onde o service é chamado (rastrear callers)

## 🛑 Fluxo obrigatório
1. **Análise:** auditar de fato a existência da classe e seu estado
2. **Plano de correção em conjunto:** se existe → adicionar export; se não existe → decidir se cria ou remove o import
3. **Aprovação** do plano
4. **Só então** codificar


# BUG #14 — `UserPermissionForm` pode estar faltando em `core/forms/__init__.py`

## 🎯 Contexto
Projeto **Lia Linda** — `core/forms/__init__.py` re-exporta forms de arquivos como `master.py`, `role.py`, `tenant.py` para permitir:

```python
from core.forms import RoleForm, RolePermissionForm, UserPermissionForm
```

## 📍 Localização
- `core/views/tenant_view.py`:
  ```python
  from core.forms import UserPermissionForm, RolePermissionForm
  ```
- `core/forms/role.py` — onde **`RolePermissionForm`** está definido
- `core/forms/tenant.py` (?) — onde **`UserPermissionForm`** deveria estar

## 🐛 Descrição do bug
- `RolePermissionForm` foi observado em `core/forms/role.py` ✅
- `UserPermissionForm` é importado em `tenant_view.py` mas **não foi confirmado** em nenhum arquivo de forms mapeado
- Possíveis cenários:
  1. Existe em `core/forms/tenant.py` (que precisa ser auditado)
  2. Não existe e é resquício de código antigo
  3. Existe em outro nome e o import quebra silenciosamente em testes

## 💥 Impactos possíveis
1. **`ImportError`** ao acessar `/org/<slug>/user-permissions/new/`
2. Funcionalidade de override de permissão por usuário inacessível
3. Quebra do "Filosofia C" via UI

## 🔍 Investigação prévia necessária
- Auditar `core/forms/tenant.py` (ou similares) e confirmar presença/ausência
- Verificar em `core/forms/__init__.py` se há export
- Ver se há views que usam o form em runtime
- Conferir se model `UserPermission` está completo

## 🛑 Fluxo obrigatório
1. **Análise:** confirmar existência do form e do export
2. **Plano de correção em conjunto:** criar form se faltar (com base no `UserPermission` model), ou ajustar imports
3. **Aprovação** do plano
4. **Só então** codificar



# BUG #15 — `ROLES` declarativo não tem role com `scope=global`

## 🎯 Contexto
Projeto **Lia Linda** — RBAC tem 3 escopos:
- `tenant` — Roles dentro de uma Organization
- `superuser` — SystemRoles para SaaS staff (LiaFit interno)
- `global` — SystemRoles para usuários sem org (ex: cliente final da plataforma)

O `SystemRoleSlug` (em `core/constants/permissions.py`) declara:
```python
class SystemRoleSlug(models.TextChoices):
    SUPERADMIN = "superadmin", "Super Administrador"
    CLIENT     = "client",     "Cliente"  # ← global
```

E o `MemberContext` tem o método:
```python
def is_platform_client(self) -> bool:
    return SystemRoleSlug.CLIENT in self.system_roles
```

## 📍 Localização
- `core/constants/roles.py` — declarativo `ROLES`
- `core/services/bootstrap/system_roles.py` — `sync_system_roles`

## 🐛 Descrição do bug
O `ROLES` declarativo só tem entradas com `scope=tenant` e `scope=superuser`:

```python
ROLES = [
    {"slug": "owner",      "scope": "tenant", ...},
    {"slug": "admin",      "scope": "tenant", ...},
    {"slug": "manager",    "scope": "tenant", ...},
    {"slug": "member",     "scope": "tenant", ...},
    {"slug": "superadmin", "scope": "superuser", ...},
    # ❌ falta {"slug": "client", "scope": "global", ...}
]
```

A função `sync_system_roles` filtra por `system_scopes = {GLOBAL, SUPERUSER}` e só vai criar `superadmin`. O `SystemRole(slug='client', scope='global')` **não é criado automaticamente**.

## 💥 Impactos possíveis
1. Verificações `is_platform_client()` sempre retornam `False` (porque não há `UserSystemRole` com slug `client` ativo, pois o `SystemRole` nem existe)
2. Área de cliente final da plataforma fica inacessível
3. Onboarding de cliente plataforma quebra silenciosamente
4. Inconsistência entre enum (declara `CLIENT`) e bootstrap (não cria)

## 🔍 Investigação prévia necessária
- Existe fluxo real de "cliente plataforma" implementado? Ou é planejamento futuro?
- Quais permissões `client` deveria ter? (lista vazia? escopo `my-area`?)
- Como `client` é atribuído a um user — automático no signup público?

## 🛑 Fluxo obrigatório
1. **Análise:** confirmar se o domínio "cliente plataforma" está em uso
2. **Plano de correção em conjunto:** opções:
   - (a) adicionar entrada no `ROLES` com permissões adequadas
   - (b) postergar (remover `is_platform_client` e `SystemRoleSlug.CLIENT` até feature ativa)
   - (c) criar via data migration
3. **Aprovação** do plano
4. **Só então** codificar




# 🐛 Relatório de Bugs — Lia Linda SaaS

Este diretório contém **22 bugs** identificados em auditoria arquitetural do projeto Lia Linda (SaaS multi-tenant em Django 4.2 para personal trainers).

## ⚠️ Fluxo obrigatório para qualquer correção

1. **Análise** do bug em conjunto (entender contexto, impactos, dependências)
2. **Plano de correção elaborado em conjunto** — discutir abordagens, trade-offs, testes
3. **Aprovação explícita** do plano
4. **Só então** a implementação

> **Nunca pular direto para o código.** Cada arquivo de bug é projetado para ser usado como prompt em qualquer IA assistente — ele contém contexto suficiente para discutir o problema sem precisar enviar arquivos do projeto.

## 📋 Índice

### 🔴 Críticos (5)
- [BUG-01](BUG-01-saas-admin-nao-instalado.md) — App `saas_admin` referenciado mas não instalado <- Já resolvi
- [BUG-02](BUG-02-resend-password-token-inexistente.md) — `OnboardingService.resend_password_token()` não existe <- corrigido
- [BUG-03](BUG-03-typo-changer-member.md) — Typo: `settings.changer_member`<- corrigido
- [BUG-04](BUG-04-url-role-permissions-view-errada.md) — URL `role_permissions_update` aponta para view errada <- corrido
- [BUG-05](BUG-05-dashboardview-template-view-getqueryset.md) — DashboardView mistura TemplateView + ContextMixin <- corrigido

### 🟡 Importantes (10)
- [BUG-06](BUG-06-success-url-sem-namespace.md) — `success_url` sem namespace <- corrigido
- [BUG-07](BUG-07-typo-deshboard-service.md) — Typo no nome do arquivo `deshboard_service.py <- corrigido
- [BUG-08](BUG-08-comentario-cabecalho-errado.md) — Comentário de cabeçalho errado
- [BUG-09](BUG-09-login-redirect-url-hardcoded.md) — `LOGIN_REDIRECT_URL` hard-coded <- corrigido
- [BUG-10](BUG-10-logging-vazio.md) — LOGGING vazio <- corrigido
- [BUG-11](BUG-11-action-invite-vs-add-member.md) — Inconsistência `INVITE` vs `ADD` para Member
- [BUG-12](BUG-12-rolelistview-conflito-namespaces.md) — `RoleListView` em dois namespaces
- [BUG-13](BUG-13-clientprofessional-import-faltante.md) — `ClientProfessional` import faltante
- [BUG-14](BUG-14-userpermissionform-export-incerto.md) — `UserPermissionForm` export incerto
- [BUG-15](BUG-15-roles-sem-scope-global.md) — Falta role com scope=global

### 🟢 Baixas (7)
- [BUG-16](BUG-16-comentarios-cabecalho-urls.md) — Comentários cabeçalho URLs <- Já corrigi
- [BUG-17](BUG-17-marca-inconsistente.md) — Marca inconsistente (Lia Linda / LiaFit / PersonalPro) <- Já corrigi
- [BUG-18](BUG-18-codigo-comentado-morto.md) — Código comentado morto <- Já corrigi
- [BUG-19](BUG-19-allowed-hosts-sem-comentario.md) — `ALLOWED_HOSTS` sem comentário prod <- Vamos verificar esse.
- [BUG-20](BUG-20-core-urls-init-faltante.md) — `core/urls/__init__.py` faltante <- Já resolvi
- [BUG-21](BUG-21-secret-key-fraca-em-prod.md) — SECRET_KEY fraca em prod <- Já resolvi
- [BUG-22](BUG-22-deny-redirect-master-dashboard-hardcoded.md) — `_deny()` hardcoded para master:dashboard

## 🎯 Ordem sugerida de ataque

1. Críticos #3, #1, #2, #6 (quick wins, ~15min total)
2. Críticos #4, #5 (precisam discussão arquitetural)
3. Importantes em ordem de impacto
4. Baixas em sprint de polimento


## 🐛 Erro: Manager não acessa "Permissões do Papel" e "Permissões do Usuário"

**Sintoma:** Manager redirecionado para dashboard com mensagem
"Você não tem permissão para acessar esta funcionalidade".
Owner funciona normalmente.

**Causa raiz:** strings de `permission_required` apontavam para
codenames inexistentes no catálogo (`core.models.Permission`).

| View                                   | String fantasma                       |
|----------------------------------------|---------------------------------------|
| `TenantRolePermissionsView`            | `settings.view_role_permission`       |
| `TenantRolePermissionsUpdateView`      | `settings.change_rolepermission`      |
| `TenantUserPermissionsView`            | `settings.view_user_permission`       |
| `TenantUserPermissionsUpdateView`      | `settings.change_user_permission`     |

O catálogo só registra permissões para items declarados em `ItemSlug`
(`role`, `member`, `organization`, etc). Não existe `role_permission`
nem `user_permission` como itens — são views auxiliares que operam
sobre `Role` e `Member`.

**Fix:** reusar as permissões dos itens proprietários:
- `role_permission` views → `settings.{view,change}_role`
- `user_permission` views → `settings.{view,change}_member`

**Por que owner funcionava?** Owner tem `permissions: ["*"]` no
`SYSTEM_ROLES`, então `resolve_permissions("*")` injeta TODAS as
permissões do catálogo no role — incluindo qualquer codename que
viesse a existir. Manager tem permissões granulares e por isso
expôs o bug.

**Lições:**
1. Strings de permissão são pontos cegos — não há validação estática.
2. O catálogo (`core.models.Permission`) é independente do
   `django.contrib.auth.Permission`. `BaseAuthMixin` consulta apenas
   o catálogo via `MemberContext.has_permission()`.
3. Codenames seguem o formato `{module_slug}.{action}_{item_slug}`
   gerado por `ModuleItem.permission_codename()`.


