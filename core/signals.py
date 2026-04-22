# core/signals.py
"""
Signals de invalidação de cache do ContextService (RBAC).

================================================================
PROPÓSITO
================================================================
O ContextService mantém em cache o "contexto" de cada membro de
uma organização — um snapshot com:
  • roles ativas
  • permissões efetivas (union de roles + allows - denies)
  • metadados do membership

Ler esse contexto do cache é O(1). Reconstruí-lo envolve múltiplas
queries no banco. Por isso cacheamos agressivamente.

O problema: se o cache ficar *stale* (desatualizado) depois que
um admin mexe nas permissões, o usuário continua com acesso
indevido (ou bloqueado indevidamente) até o TTL expirar.

SOLUÇÃO: sempre que algo que compõe o contexto mudar, disparamos
um signal que INVALIDA a entrada de cache correspondente. Na
próxima leitura, o contexto é reconstruído fresco do banco.

================================================================
ESCOPO ATUAL (Passo 3.3)
================================================================
Este arquivo cobre apenas `UserPermission` (allow/deny individuais).

Outros modelos que afetam o contexto e ainda precisam de signals
(Passo 3.4):
  • RolePermission         → afeta todos os membros com a role
  • OrganizationMember     → afeta o membro específico
  • Role (delete/rename)   → edge cases

================================================================
GARANTIAS
================================================================
  ✅ Invalidação síncrona (post_save/post_delete rodam na mesma
     transação do ORM).
  ✅ Escopo mínimo: invalida apenas (user, organization) afetado.
  ✅ Idempotente: invalidar uma chave inexistente é no-op seguro.

Validação ponta-a-ponta: ver `docs/rbac/passo-3.3-validacao.md`.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import UserPermission
from core.services.context_service import ContextService


# ─────────────────────────────────────────────────────────────────
# UserPermission (allow / deny individuais por usuário+organização)
# ─────────────────────────────────────────────────────────────────
@receiver(post_save, sender=UserPermission)
def invalidate_on_user_permission_saved(sender, instance, **kwargs):
    """
    Invalida o cache quando uma UserPermission é criada ou alterada.

    Disparado em:
      • Criação de novo allow/deny individual.
      • Alteração do campo `effect` (allow ↔ deny).
      • Qualquer `.save()` na instância (mesmo sem mudança real).

    Args:
        sender: Classe UserPermission (não usado).
        instance: A instância salva. Usamos `user_id` e
                  `organization_id` para identificar qual cache
                  deve ser invalidado.
        **kwargs: `created`, `raw`, `using`, `update_fields` (ignorados).

    Efeito:
        Remove a chave de cache do par (user_id, organization_id).
        Próxima chamada a `ContextService.build_member_context`
        reconstrói do banco.
    """
    ContextService.invalidate(instance.user_id, instance.organization_id)


@receiver(post_delete, sender=UserPermission)
def invalidate_on_user_permission_deleted(sender, instance, **kwargs):
    """
    Invalida o cache quando uma UserPermission é deletada.

    Cenário típico: admin remove um `deny` individual, esperando
    que o usuário recupere imediatamente a permissão vinda da role.

    Args:
        sender: Classe UserPermission (não usado).
        instance: A instância deletada. Seus campos ainda estão
                  acessíveis em memória neste ponto.
        **kwargs: `using` (ignorado).

    Efeito:
        Mesma lógica do post_save: remove a chave do par
        (user_id, organization_id).
    """
    ContextService.invalidate(instance.user_id, instance.organization_id)
