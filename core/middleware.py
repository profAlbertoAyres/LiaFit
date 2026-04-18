import re

from django.http import HttpResponseForbidden

from core.services.context_service import ContextService
from account.models import Organization, OrganizationMember


class RequestContext:
    """Objeto leve que carrega o contexto do request."""
    organization = None
    membership = None
    professional = None
    roles = []
    modules = []
    permissions = []


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
        # Inicializa contexto limpo
        request.context = RequestContext()
        request.context.user = request.user

        # Rotas isentas de tudo
        if self._is_exempt(request.path):
            return self.get_response(request)

        # Usuário não logado não precisa de contexto
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Rotas que não exigem tenant (mas user está logado)
        if self._is_no_tenant(request.path):
            return self.get_response(request)

        # ── RESOLUÇÃO DE TENANT ──────────────────────────
        org_slug = self._extract_slug(request.path)
        if not org_slug:
            return self.get_response(request)

        # 1. Busca a organização pelo slug
        try:
            organization = Organization.objects.get(
                slug=org_slug,
                is_active=True,
            )
        except Organization.DoesNotExist:
            return HttpResponseForbidden(
                "Organização não encontrada ou inativa."
            )

        # 2. Busca o membership do usuário nessa organização
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

        # 3. Monta o contexto
        request.context.organization = organization
        request.context.membership = membership
        request.context.professional = getattr(
            membership, 'professional_profile', None
        )

        # 4. RBAC
        roles = ContextService.load_roles(membership)
        modules = ContextService.load_modules(organization)
        permissions = ContextService.load_permissions(roles, modules)

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions

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
