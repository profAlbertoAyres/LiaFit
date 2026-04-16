from core.context import RequestContext
from core.services.context_service import ContextService
from account.models import OrganizationMember, Professional


class SaaSContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.context = RequestContext()
        request.context.user = request.user

        if not request.user.is_authenticated:
            return self.get_response(request)

        # TENANT — busca o primeiro vínculo ativo do usuário
        membership = (
            OrganizationMember.objects
            .filter(user=request.user, is_active=True)
            .select_related('organization', 'role')
            .first()
        )

        if not membership:
            request.context.organization = None
            request.context.roles = set()
            request.context.modules = set()
            request.context.permissions = set()
            return self.get_response(request)

        org = membership.organization
        request.context.organization = org

        # PROFISSIONAL (se tiver perfil de profissional)
        request.context.professional = getattr(
            membership, 'professional_profile', None
        )

        # RBAC
        roles = ContextService.load_roles(request.user, org)
        modules = ContextService.load_modules(org)
        permissions = ContextService.load_permissions(roles, modules)

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions

        return self.get_response(request)
