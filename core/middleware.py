import re

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from core.services.context_service import ContextService
from account.models import Organization, OrganizationMember
from core.services.space_constants_service import detect_current_space
from core.services.space_hub_service import SpaceHubService

ORG_SLUG_PATTERN = re.compile(r'^/org/(?P<org_slug>[\w-]+)/')


class SaaSContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        request.user_role = None
        request.context = None
        request.current_space = detect_current_space(request.path)

        org_slug = self._get_org_slug(request)
        if not org_slug:
            if request.user.is_authenticated:
                request.context = ContextService.build_system_context(request.user)
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(f"{reverse('auth:login')}?next={request.path}")

        org = Organization.objects.filter(slug=org_slug, is_active=True).first()
        if not org:
            messages.error(request, 'Organização não encontrada ou inativa.')
            return redirect(SpaceHubService.get_safe_redirect_url(request))

        ctx = self._build_context(request.user, org)
        if not ctx:
            messages.error(request, 'Você não tem acesso a esta organização.')
            return redirect(SpaceHubService.get_safe_redirect_url(request))

        request.tenant = org
        request.context = ctx
        # request.session['last_org_slug'] = org_slug

        if ctx.membership:
            request.user_role = ctx.membership.roles.order_by('-level').first()

        return self.get_response(request)

    def _get_org_slug(self, request):
        match = ORG_SLUG_PATTERN.match(request.path)
        return match.group('org_slug') if match else None

    def _build_context(self, user, org):

        membership = OrganizationMember.objects.filter(
            user=user, organization=org, is_active=True,
        ).first()
        if not membership:
            return None

        return ContextService.build_member_context(user, org, membership)
