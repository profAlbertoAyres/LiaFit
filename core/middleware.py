import re

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from core.models import OrganizationModule, Permission
from core.services.context_service import ContextService, MemberContext
from core.services.permission_service import is_saas_staff  # 🆕
from account.models import Organization, OrganizationMember

ORG_SLUG_PATTERN = re.compile(r'^/org/(?P<org_slug>[\w-]+)/')


class SaaSContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        request.user_role = None
        request.context = None

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
            return redirect('dashboard')

        ctx = self._build_context(request.user, org)
        if not ctx:
            messages.error(request, 'Você não tem acesso a esta organização.')
            return redirect('dashboard')

        request.tenant = org
        request.context = ctx
        request.session['last_org_slug'] = org_slug

        if ctx.membership:
            request.user_role = ctx.membership.roles.order_by('-level').first()

        return self.get_response(request)

    def _get_org_slug(self, request):
        match = ORG_SLUG_PATTERN.match(request.path)
        return match.group('org_slug') if match else None

    def _build_context(self, user, org):
        # 🆕 SaaS staff (você + equipe interna) entra em qualquer org
        # para dar suporte técnico, com TODAS as permissões.
        if is_saas_staff(user):
            return MemberContext(
                user=user,
                organization=org,
                membership=None,
                roles={'saas_staff'},
                modules=set(
                    OrganizationModule.objects
                    .filter(organization=org, is_active=True)
                    .values_list('module__slug', flat=True)
                ),
                permissions=set(
                    Permission.objects.values_list('codename', flat=True)
                ),
                system_roles=set(
                    user.system_roles
                    .filter(is_active=True, system_role__is_active=True)
                    .values_list('system_role__slug', flat=True)
                ),
            )

        membership = OrganizationMember.objects.filter(
            user=user, organization=org, is_active=True,
        ).first()
        if not membership:
            return None

        return ContextService.build_member_context(user, org, membership)
