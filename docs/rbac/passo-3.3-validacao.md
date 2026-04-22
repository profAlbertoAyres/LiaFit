# Passo 3.3 — Validação dos signals de `UserPermission`

- **Data da execução:** 2026-04-22
- **Executado por:** Alberto
- **Ambiente:** desenvolvimento local (SQLite, `python manage.py shell`)
- **Objetivo:** Provar que `post_save` e `post_delete` de `UserPermission`
  invalidam corretamente o cache do `ContextService`.
- **Relacionado:** [ADR-001](./adr-001-cache-invalidation.md)

---

## 1. Pré-condições

- [x] `core/signals.py` com receivers de `UserPermission` implementados.
- [x] `core/apps.py` importando `core.signals` em `ready()`.
- [x] `ContextService.invalidate(user_id, organization_id)` implementado.
- [x] `python manage.py check` sem erros.

---

## 2. Setup do cenário de teste

### Atores
- **Usuário:** `alberto` (id de teste)
- **Organização:** `Academia Teste` (id de teste)
- **Role:** `instructor` com permissão `add_transaction`
- **Membership:** `alberto` é membro da org com role `instructor`

### Estado inicial esperado
- `alberto` tem `add_transaction` via role `instructor`.
- Nenhum `UserPermission` individual cadastrado para `alberto`.

---

## 3. Execução do teste

### Fase A — Cache populado (baseline)

```python
from core.services.context_service import ContextService

ctx = ContextService.get_or_build(user_id=<ID_ALBERTO>, organization_id=<ID_ORG>)
print("add_transaction" in ctx.permissions)
# Esperado: True
```

**Resultado:** ✅ `True` — permissão vinda da role está presente.

---

### Fase B — Criar `deny` individual → signal `post_save`

```python
from core.models import UserPermission, Permission

perm = Permission.objects.get(codename="add_transaction")

UserPermission.objects.create(
    user_id=<ID_ALBERTO>,
    organization_id=<ID_ORG>,
    permission=perm,
    effect="deny",
)
```

**Ação esperada do signal:**
`invalidate_on_user_permission_saved` dispara →
`ContextService.invalidate(<ID_ALBERTO>, <ID_ORG>)` é chamado.

**Verificação:**

```python
ctx2 = ContextService.get_or_build(user_id=<ID_ALBERTO>, organization_id=<ID_ORG>)
print("add_transaction" in ctx2.permissions)
# Esperado: False (deny individual sobrepõe allow da role)
```

**Resultado:** ✅ `False` — contexto reconstruído do banco, deny aplicado.

---

### Fase C — Deletar o `deny` → signal `post_delete`

```python
UserPermission.objects.filter(
    user_id=<ID_ALBERTO>,
    organization_id=<ID_ORG>,
    permission=perm,
).delete()
```

**Ação esperada do signal:**
`invalidate_on_user_permission_deleted` dispara →
cache invalidado novamente.

**Verificação:**

```python
ctx3 = ContextService.get_or_build(user_id=<ID_ALBERTO>, organization_id=<ID_ORG>)
print("add_transaction" in ctx3.permissions)
# Esperado: True (voltou a vir da role)
```

**Resultado:** ✅ `True` — permissão restaurada, contexto fresco.

---

## 4. Resumo

| Fase | Ação | Signal | Esperado | Resultado |
|---|---|---|---|---|
| A | Leitura inicial | — | `add_transaction ∈ ctx` | ✅ |
| B | `create(deny)` | `post_save` | `add_transaction ∉ ctx` | ✅ |
| C | `delete()` | `post_delete` | `add_transaction ∈ ctx` | ✅ |

**Conclusão:** ✅ Signals de `UserPermission` funcionam como projetado.
Cache é invalidado tanto na criação/alteração quanto na exclusão.

---

## 5. Observações e pontos de atenção

- 🟡 **Teste via `bulk_create` não executado.** Django não dispara signals
  em operações bulk. Se no futuro houver fluxo com bulk, invalidar
  manualmente. Já documentado no ADR-001 §4.
- 🟡 **Teste concorrente não executado.** Cenários de race condition
  (duas requests simultâneas, uma lendo cache enquanto outra salva)
  não foram cobertos neste passo. Ficam para fase de testes de carga.
- 🟢 **Próximo passo (3.4):** replicar padrão para `RolePermission`,
  `OrganizationMember` (M2M de roles) e `Role`.

---

## 6. Como reproduzir

```bash
# 1. Ativar venv
.venv\Scripts\activate

# 2. Abrir shell Django
python manage.py shell

# 3. Executar os blocos das fases A, B, C acima, em sequência.
```

Caso algum resultado divirja do esperado, investigar:
1. `core/apps.py` está importando `core.signals`?
2. `CoreConfig` está em `INSTALLED_APPS`?
3. `ContextService.invalidate()` realmente remove a chave do backend de cache configurado em `settings.CACHES`?
