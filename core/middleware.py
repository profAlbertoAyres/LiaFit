from core.context import RequestContext
from core.services.context_service import ContextService
from account.models import Professional, UserOrganization


class SaaSContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.context = RequestContext()
        request.context.user = request.user

        if not request.user.is_authenticated:
            return self.get_response(request)

        request.context.profile = getattr(request.user, "profile", None)

        # TENANT
        user_org = (
            UserOrganization.objects
            .filter(user=request.user, is_active=True)
            .select_related("organization", "role")
            .first()
        )

        if not user_org:
            request.context.organization = None
            request.context.roles = []
            request.context.modules = []
            request.context.permissions = []
            return self.get_response(request)

        org = user_org.organization

        request.context.organization = org

        # PROFISSIONAL
        request.context.professional = Professional.objects.filter(
            user=request.user,
            organization=org
        ).first()

        # RBAC (ROLE OBJECTS)
        roles = ContextService.load_roles(request.user, org)
        modules = ContextService.load_modules(org)
        permissions = ContextService.load_permissions(roles, modules)

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions

        return self.get_response(request)