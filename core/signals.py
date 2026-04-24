# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Organization
from core.services.bootstrap import bootstrap_organization_core


@receiver(post_save, sender=Organization)
def bootstrap_org_core_modules(sender, instance, created, **kwargs):
    """
    Quando uma Organization é criada, ativa automaticamente os módulos
    is_core=True e concede suas permissions ao Role de maior nível.

    Observação: roda também quando você edita a org, mas é idempotente
    (update_or_create + get_or_create), então é barato.
    """
    if not created:
        return
    bootstrap_organization_core(instance)
