from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from account.models.member import OrganizationMember
from core.models.user_permission import UserPermission
from core.models.organization_module import OrganizationModule
from core.models.user_system_role import UserSystemRole
from core.models.role_permission import RolePermission
from core.services.context_service import ContextService


@receiver([post_save, post_delete], sender=UserPermission)
def invalidate_on_user_permission(sender, instance, **kwargs):
    ContextService.invalidate(instance.user_id, instance.organization_id)


@receiver([post_save, post_delete], sender=OrganizationMember)
def invalidate_on_membership(sender, instance, **kwargs):
    ContextService.invalidate(instance.user_id, instance.organization_id)


@receiver(m2m_changed, sender=OrganizationMember.roles.through)
def invalidate_on_membership_roles(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        ContextService.invalidate(instance.user_id, instance.organization_id)


@receiver([post_save, post_delete], sender=OrganizationModule)
def invalidate_on_org_module(sender, instance, **kwargs):
    for user_id in OrganizationMember.objects.filter(
        organization_id=instance.organization_id
    ).values_list('user_id', flat=True):
        ContextService.invalidate(user_id, instance.organization_id)


@receiver([post_save, post_delete], sender=RolePermission)
def invalidate_on_role_permission(sender, instance, **kwargs):
    for user_id in OrganizationMember.objects.filter(
        organization_id=instance.organization_id,
        roles=instance.role_id,
    ).values_list('user_id', flat=True):
        ContextService.invalidate(user_id, instance.organization_id)


@receiver([post_save, post_delete], sender=UserSystemRole)
def invalidate_on_system_role(sender, instance, **kwargs):
    ContextService.invalidate_system(instance.user_id)
    for org_id in OrganizationMember.objects.filter(
        user_id=instance.user_id
    ).values_list('organization_id', flat=True):
        ContextService.invalidate(instance.user_id, org_id)
