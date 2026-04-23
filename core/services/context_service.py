from dataclasses import dataclass, field
from typing import Set, Optional, TYPE_CHECKING

from django.core.cache import cache
from django.conf import settings

from core.models import Permission, UserPermission
from core.models.role_permission import RolePermission
from core.models.organization_module import OrganizationModule

if TYPE_CHECKING:
    from core.models import Organization, OrganizationMember


ADMIN_ROLE_SLUGS = frozenset({"owner", "admin"})


@dataclass
class MemberContext:
    user: object
    organization: object
    membership: object
    roles: Set[str] = field(default_factory=set)
    modules: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)
    professional: Optional[object] = None

    def has_permission(self, codename: str) -> bool:
        return codename in self.permissions

    def has_all_permissions(self, *codenames: str) -> bool:
        return all(c in self.permissions for c in codenames)

    def has_any_permission(self, *codenames: str) -> bool:
        return any(c in self.permissions for c in codenames)

    def has_module(self, slug: str) -> bool:
        return slug in self.modules

    def has_role(self, slug: str) -> bool:
        return slug in self.roles

    def is_admin(self) -> bool:
        return bool(self.roles & ADMIN_ROLE_SLUGS)


@dataclass
class ClientContext:
    user: object
    client: object


class ContextService:
    """
    Calcula o contexto RBAC de um usuário numa organização, com cache.

    Precedência de permissões:
        final = (role_perms ∪ allow_perms) − deny_perms
    """

    # ---------- API PÚBLICA ----------

    @classmethod
    def build_member_context(cls, user, organization, membership) -> MemberContext:
        cache_key = cls._cache_key(user.id, organization.id)
        cached = cache.get(cache_key)

        if cached is not None:
            # 🔥 HOT PATH
            return MemberContext(
                user=user,
                organization=organization,
                membership=membership,
                roles=cached['roles'],
                modules=cached['modules'],
                permissions=cached['permissions'],
                professional=getattr(membership, 'professional_profile', None),
            )

        # ❄️ COLD PATH
        roles = cls.load_roles(membership)
        modules = cls.load_modules(organization)
        permissions = cls.load_permissions(user, organization, roles, modules)

        cache.set(
            cache_key,
            {
                'roles': roles,
                'modules': modules,
                'permissions': permissions,
            },
            timeout=settings.RBAC_CACHE_TTL,
        )

        return MemberContext(
            user=user,
            organization=organization,
            membership=membership,
            roles=roles,
            modules=modules,
            permissions=permissions,
            professional=getattr(membership, 'professional_profile', None),
        )

    @classmethod
    def build_client_context(cls, user, client) -> ClientContext:
        return ClientContext(user=user, client=client)

    # ---------- CACHE HELPERS ----------

    @staticmethod
    def _cache_key(user_id: int, organization_id: int) -> str:
        v = settings.RBAC_CACHE_VERSION
        return f'rbac:ctx:v{v}:u{user_id}:o{organization_id}'

    @classmethod
    def invalidate(cls, user_id: int, organization_id: int) -> None:
        cache.delete(cls._cache_key(user_id, organization_id))

    # ---------- BLOCOS DE CONSTRUÇÃO ----------

    @staticmethod
    def load_roles(membership) -> Set[str]:
        return set(membership.roles.values_list('slug', flat=True))

    @staticmethod
    def load_modules(organization) -> Set[str]:
        return set(
            OrganizationModule.objects.filter(
                organization=organization,
                is_active=True,
            ).values_list('module__slug', flat=True)
        )

    @staticmethod
    def load_permissions(user, organization, roles: Set[str], modules: Set[str]) -> Set[str]:
        role_perms = set(
            RolePermission.objects.filter(
                role__slug__in=roles,
                permission__item__module__slug__in=modules,
            ).values_list('permission__codename', flat=True)
        )

        allow_perms = set(
            Permission.objects.filter(
                user_permissions__user=user,
                user_permissions__organization=organization,
                user_permissions__effect=UserPermission.Effect.ALLOW,
                item__module__slug__in=modules,
            ).values_list('codename', flat=True)
        )

        deny_perms = set(
            Permission.objects.filter(
                user_permissions__user=user,
                user_permissions__organization=organization,
                user_permissions__effect=UserPermission.Effect.DENY,
            ).values_list('codename', flat=True)
        )

        return (role_perms | allow_perms) - deny_perms
