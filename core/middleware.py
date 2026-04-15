from core.context import RequestContext
from core.services.context_service import ContextService
from account.models import Professional


class SaaSContextMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.context = RequestContext()
        request.context.user = request.user

        if not request.user.is_authenticated:
            return self.get_response(request)

        profile = getattr(request.user, "profile", None)
        request.context.profile = profile

        if not profile or not profile.current_organization:
            return self.get_response(request)

        org = profile.current_organization

        request.context.organization = org

        request.context.professional = Professional.objects.filter(
            user=request.user,
            organization=org
        ).first()

        roles = ContextService.load_roles(user, org)
        modules = ContextService.load_modules(org)
        permissions = ContextService.load_permissions(roles, modules)

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions

        request.context.roles = roles
        request.context.modules = modules
        request.context.permissions = permissions
        print("=== CONTEXT DEBUG ===")
        print("USER:", request.user)
        print("ORG:", getattr(request.context, "organization", None))
        print("ROLES:", getattr(request.context, "roles", None))
        print("=====================")
        print("CTX:", request.context.__dict__)
        return self.get_response(request)