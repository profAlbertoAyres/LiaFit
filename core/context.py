import re

from core.services.context_service import ContextService
from account.models import Organization, OrganizationMember


# Regex pra extrair o slug da URL: /org/<slug>/...
ORG_SLUG_PATTERN = re.compile(r'^/org/(?P<org_slug>[\w-]+)/')

# Rotas que não precisam de tenant
TENANT_EXEMPT_PREFIXES = (
    '/admin/',
    '/api/auth/',
    '/health/',
)


class SaaSContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.context = RequestContext()
        request.context.user = request.user

        # Rotas isentas de tenant
        if self._is_exempt(request.path):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        # 1. Extrai o slug da URL
        org_slug = self._extract_slug(request.path)
        if not org_slug:
            return self.get_response(request)

        # 2. Busca a organização pelo slug
        try:
            organization = Organization.objects.get(
                slug=org_slug,
                is_active=True,
            )
        except Organization.DoesNotExist:
            return self.get_response(request)

        # 3. Busca o membership do usuário nessa organização
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
            return self.get_response(request)

        # 4. Monta o contexto
        request.context.organization = organization
        request.context.professional = getattr(
            membership, 'professional_profile', None
        )

        # 5. RBAC
        roles = ContextService.load_roles(membership)
        modules = ContextService.load_modules(organization)
        permissions = ContextService.load_permissions(roles, modules)

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions

        return self.get_response(request)

    @staticmethod
    def _is_exempt(path):
        return any(path.startswith(prefix) for prefix in TENANT_EXEMPT_PREFIXES)

    @staticmethod
    def _extract_slug(path):
        match = ORG_SLUG_PATTERN.match(path)
        return match.group('org_slug') if match else None
