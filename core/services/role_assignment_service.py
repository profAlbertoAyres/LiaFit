# account/services/role_assignment_service.py
from django.db import transaction

from account.exceptions import (
    RoleAssignmentDuplicateError,
    RoleAssignmentHierarchyError,
    RoleAssignmentLastRoleError,
    RoleAssignmentNotFoundError,
    RoleAssignmentOwnerError,
    RoleAssignmentSelfError,
    UndoAlreadyDoneError,
    UndoWindowExpiredError,
)
from core.constants.role_assignment_constant import is_within_undo_window
from core.models import RoleAssignmentLog
from core.services.context_service import ContextService


class RoleAssignmentService:

    @classmethod
    @transaction.atomic
    def assign(cls, *, membership, role, actor, actor_membership):
        cls._validate(membership, role, actor, actor_membership)

        if membership.roles.filter(pk=role.pk).exists():
            raise RoleAssignmentDuplicateError()

        membership.roles.add(role)
        log = RoleAssignmentLog.objects.create(
            organization=membership.organization,
            membership=membership,
            role=role,
            action=RoleAssignmentLog.Action.ASSIGN,
            actor=actor,
        )
        cls._invalidate_cache(membership)
        return log

    @classmethod
    @transaction.atomic
    def revoke(cls, *, membership, role, actor, actor_membership):
        cls._validate(membership, role, actor, actor_membership)

        if not membership.roles.filter(pk=role.pk).exists():
            raise RoleAssignmentNotFoundError("Membro não possui este papel.")

        if membership.roles.count() <= 1:
            raise RoleAssignmentLastRoleError()

        membership.roles.remove(role)
        log = RoleAssignmentLog.objects.create(
            organization=membership.organization,
            membership=membership,
            role=role,
            action=RoleAssignmentLog.Action.REVOKE,
            actor=actor,
        )
        cls._invalidate_cache(membership)
        return log

    @classmethod
    @transaction.atomic
    def undo(cls, *, log, actor, actor_membership):
        if log.is_undone:
            raise UndoAlreadyDoneError()

        if not is_within_undo_window(log.created_at):
            raise UndoWindowExpiredError()

        cls._validate(log.membership, log.role, actor, actor_membership)

        if log.action == RoleAssignmentLog.Action.ASSIGN:
            log.membership.roles.remove(log.role)
        else:
            log.membership.roles.add(log.role)

        log.mark_undone(actor)
        cls._invalidate_cache(log.membership)
        return log

    # ──────────────── VALIDATIONS ────────────────

    @classmethod
    def _validate(cls, membership, role, actor, actor_membership):
        if membership.user_id == actor.id and not actor.is_superuser:
            raise RoleAssignmentSelfError()

        if membership.organization.owner_id == membership.user_id:
            raise RoleAssignmentOwnerError()

        if actor.is_superuser:
            return

        actor_level = cls._highest_level(actor_membership)
        role_level = role.level or 0

        if role_level >= actor_level:
            raise RoleAssignmentHierarchyError(
                f"Você (nível {actor_level}) não pode mexer em papéis de nível {role_level}."
            )

        target_level = cls._highest_level(membership)
        if target_level >= actor_level:
            raise RoleAssignmentHierarchyError(
                f"Membro alvo tem nível {target_level}, igual ou superior ao seu ({actor_level})."
            )

    @staticmethod
    def _highest_level(membership):
        if not membership:
            return 0
        return max(membership.roles.values_list("level", flat=True), default=0)

    @staticmethod
    def _invalidate_cache(membership):
        ContextService.invalidate(
            user_id=membership.user_id,
            organization_id=membership.organization_id,
        )
