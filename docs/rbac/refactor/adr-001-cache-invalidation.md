# ADR-001: Invalidação de cache do ContextService via Django Signals

- **Status:** ✅ Aceito
- **Data:** 2026-04-22
- **Autor:** Alberto
- **Escopo:** Sistema RBAC do LiaFit (módulo `core`)

---

## 1. Contexto

O `ContextService` é o ponto central de autorização do LiaFit. Para cada
par `(user, organization)` ele constrói um **contexto** contendo:

- Roles ativas do membro naquela organização
- Permissões efetivas (união das roles + `allow`s individuais − `deny`s individuais)
- Metadados do `OrganizationMember` (status, data de entrada, etc.)

Esse contexto é consultado em **toda requisição autenticada** para decidir
se o usuário pode executar uma ação. Reconstruí-lo envolve múltiplas
queries (joins em `OrganizationMember`, `Role`, `RolePermission`,
`UserPermission`, `Permission`).

Para evitar essa sobrecarga, o contexto é **cacheado** por par
`(user_id, organization_id)`.

### Problema

Cache agressivo → **risco de stale data**:

- Admin revoga uma permissão de um funcionário → funcionário continua com
  acesso indevido até o TTL expirar.
- Admin concede permissão → funcionário recebe "permissão negada" mesmo
  após a liberação.

Em sistemas RBAC, **staleness de permissões é risco de segurança**,
não apenas UX ruim.

---

## 2. Decisão

**Adotamos Django Signals (`post_save` / `post_delete`) como mecanismo
de invalidação automática do cache do ContextService.**

Sempre que um modelo que compõe o contexto é alterado, um receiver é
disparado e chama `ContextService.invalidate(user_id, organization_id)`.

### Modelos cobertos

| Modelo | Evento | Escopo da invalidação | Status |
|---|---|---|---|
| `UserPermission` | `post_save`, `post_delete` | `(user, org)` específico | ✅ Implementado (Passo 3.3) |
| `RolePermission` | `post_save`, `post_delete` | Todos os membros com a role | 🔜 Passo 3.4 |
| `OrganizationMember.roles` (M2M) | `m2m_changed` | `(user, org)` específico | 🔜 Passo 3.4 |
| `Role` | `post_delete` | Todos os membros da org | 🔜 Passo 3.4 |

### Registro dos signals

Feito em `core/apps.py` via `CoreConfig.ready()`, que importa
`core.signals` como side-effect para ativar os decorators `@receiver`.

---

## 3. Alternativas consideradas

### ❌ A) Invalidação manual nas views/services
Cada view que mexe em permissões chamaria `ContextService.invalidate()`
explicitamente.

- **Contra:** Fácil de esquecer. Basta uma view nova mexer em
  `UserPermission` sem chamar `invalidate()` → bug silencioso de segurança.
- **Contra:** Django Admin, shells, comandos de management, migrations
  de dados — todos precisariam lembrar de invalidar.

### ❌ B) TTL curto (ex.: 30 segundos)
Abandonar invalidação explícita e confiar em expiração rápida.

- **Contra:** Janela de 30s com permissão stale ainda é risco de segurança.
- **Contra:** Derrota o propósito do cache (hit rate despenca).

### ❌ C) Cache-aside com versionamento
Guardar um "version counter" por organização e incluir no cache key.

- **Contra:** Complexidade alta para ganho marginal.
- **Contra:** Requer infra adicional (counter atômico).

### ✅ D) Signals (escolhida)
- **Pró:** Impossível esquecer — funciona para qualquer origem de escrita
  (views, admin, shell, migrations, scripts).
- **Pró:** Escopo mínimo de invalidação.
- **Pró:** Zero infra adicional (Django já fornece).
- **Contra:** Acoplamento implícito — signals são "ação à distância".
  Mitigado com docstrings claras e este ADR.

---

## 4. Consequências

### ✅ Positivas
- **Consistência forte:** qualquer mudança em permissões é refletida na
  próxima leitura, em qualquer caminho de escrita.
- **Simplicidade:** código de negócio não precisa conhecer o cache.
- **Testabilidade:** signals podem ser desabilitados em testes que não
  precisam deles.

### ⚠️ Negativas / Trade-offs
- **Ação à distância:** um dev lendo uma view não vê que salvar
  `UserPermission` dispara invalidação. **Mitigação:** docstring no topo
  de `signals.py` + este ADR.
- **Import side-effect em `apps.py`:** o `from core import signals`
  parece "unused" para linters. **Mitigação:** comentário `# noqa: F401`
  e docstring explicando.
- **Overhead em escrita em massa:** `bulk_create` / `bulk_update`
  **não disparam signals**. **Mitigação:** documentado; se usarmos bulk
  no futuro, chamar `ContextService.invalidate()` manualmente.

---

## 5. Validação

Teste ponta-a-ponta executado em shell (ver
`docs/rbac/passo-3.3-validacao.md`):

1. Cache populado com permissão `add_transaction` via role.
2. Criado `UserPermission(effect=deny)` → signal `post_save` disparou →
   permissão desapareceu do contexto rebuildado.
3. Deletado o `UserPermission` → signal `post_delete` disparou →
   permissão voltou ao contexto.

**Resultado:** ✅ ambos os caminhos validados.

---

## 6. Referências

- [Django Signals docs](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Michael Nygard — Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- Código: `core/signals.py`, `core/apps.py`, `core/services/context_service.py`
