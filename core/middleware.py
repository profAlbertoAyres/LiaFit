import re

from django.http import HttpResponseForbidden

from core.services.context_service import ContextService
from account.models import Organization, OrganizationMember


class RequestContext:
    organization = None
    membership = None
    professional = None
    client = None
    roles: set = frozenset()
    modules: set = frozenset()
    permissions: set = frozenset()
    member_ctx = None


# Regex pra extrair o slug da URL: /org/<slug>/...
ORG_SLUG_PATTERN = re.compile(r'^/org/(?P<org_slug>[\w-]+)/')

# Rotas completamente isentas (públicas, admin, etc.)
TENANT_EXEMPT_PREFIXES = (
    '/admin/',
    '/auth/',
    '/api/auth/',
    '/health/',
)

# Rotas que não precisam de tenant, mas user pode estar logado
NO_TENANT_REQUIRED = (
    '/manage/',
    '/post-login/',
)


class SaaSContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.context = RequestContext()
        request.context.user = request.user

        if self._is_exempt(request.path):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        if hasattr(request.user, 'client_profile'):
            request.context.client = request.user.client_profile

        if self._is_no_tenant(request.path):
            return self.get_response(request)

        org_slug = self._extract_slug(request.path)
        if not org_slug:
            return self.get_response(request)

        try:
            organization = Organization.objects.get(
                slug=org_slug,
                is_active=True,
            )
        except Organization.DoesNotExist:
            return HttpResponseForbidden(
                "Organização não encontrada ou inativa."
            )

        membership = (
            OrganizationMember.objects
            .filter(
                user=request.user,
                organization=organization,
                is_active=True,
            )
            .select_related('organization')
            .prefetch_related('roles')
            .first()
        )

        if not membership:
            return HttpResponseForbidden(
                "Você não tem acesso a esta organização."
            )

        # 3 + 4. Monta contexto completo de uma vez
        member_ctx = ContextService.build_member_context(
            user=request.user,
            organization=organization,
            membership=membership,
        )

        request.context.member_ctx = member_ctx
        request.context.organization = member_ctx.organization
        request.context.membership = member_ctx.membership
        request.context.professional = member_ctx.professional
        request.context.roles = member_ctx.roles
        request.context.modules = member_ctx.modules
        request.context.permissions = member_ctx.permissions

        # 5. Salva última org na sessão (para redirect pós-login)
        request.session['last_org_slug'] = org_slug

        return self.get_response(request)

    @staticmethod
    def _is_exempt(path):
        """Rotas completamente isentas."""
        if path == '/':
            return True
        return any(
            path.startswith(prefix)
            for prefix in TENANT_EXEMPT_PREFIXES
        )

    @staticmethod
    def _is_no_tenant(path):
        """Rotas que não precisam de tenant mas user pode estar logado."""
        return any(path.startswith(prefix) for prefix in NO_TENANT_REQUIRED)

    @staticmethod
    def _extract_slug(path):
        match = ORG_SLUG_PATTERN.match(path)
        return match.group('org_slug') if match else None
