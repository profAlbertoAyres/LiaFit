# import re
# from dataclasses import dataclass, field
# from typing import Optional, Set
#
# from django.contrib import messages
# from django.http import HttpResponseForbidden
# from django.shortcuts import redirect
# from django.urls import reverse
#
# from core.models import OrganizationModule, Permission
# from core.services.context_service import ContextService, MemberContext
# from account.models import Organization, OrganizationMember
#
#
# class RequestContext:
#     def __init__(
#             self,
#             organization=None,
#             membership=None,
#             professional=None,
#             client=None,
#             roles=None,
#             modules=None,
#             permissions=None,
#             member_ctx=None,
#     ):
#         self.organization = organization
#         self.membership = membership
#         self.professional = professional
#         self.client = client
#         self.roles = roles if roles is not None else set()
#         self.modules = modules if modules is not None else set()
#         self.permissions = permissions if permissions is not None else set()
#         self.member_ctx = member_ctx
#
# # Regex pra extrair o slug da URL: /org/<slug>/...
# ORG_SLUG_PATTERN = re.compile(r'^/org/(?P<org_slug>[\w-]+)/')
#
# # Rotas completamente isentas (públicas, admin, etc.)
# TENANT_EXEMPT_PREFIXES = (
#     '/admin/',
#     '/auth/',
#     '/api/auth/',
#     '/health/',
# )
#
# # Rotas que não precisam de tenant, mas user pode estar logado
# NO_TENANT_REQUIRED = (
#     '/manage/',
#     '/post-login/',
# )
#
#
# class SaaSContextMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         # ✅ Default: sem contexto
#         request.tenant = None
#         request.user_role = None
#         request.context = None
#
#         org_slug = request.resolver_match.kwargs.get('org_slug') \
#             if request.resolver_match else None
#
#         # Rota não-tenant → segue sem contexto
#         if not org_slug:
#             return self.get_response(request)
#
#         # Rota tenant → precisa de user autenticado
#         if not request.user.is_authenticated:
#             return redirect(f"{reverse('auth:login')}?next={request.path}")
#
#         # Busca org ativa
#         try:
#             org = Organization.objects.get(slug=org_slug, is_active=True)
#         except Organization.DoesNotExist:
#             messages.error(request, 'Organização não encontrada ou inativa.')
#             return redirect('post_login')  # ✅ rota NEUTRA, sem tenant
#
#         # Superuser bypassa membership
#         if request.user.is_superuser:
#             request.tenant = org
#             request.context = MemberContext(
#                 user=request.user,
#                 organization=org,
#                 membership=None,
#                 roles={"owner"},  # ou set() + flag is_superuser
#                 modules=set(  # superuser vê todos módulos ativos
#                     OrganizationModule.objects
#                     .filter(organization=org, is_active=True)
#                     .values_list('module__slug', flat=True)
#                 ),
#                 permissions=set(  # ou um set especial "*"
#                     Permission.objects.values_list('codename', flat=True)
#                 ),
#             )
#             request.session['last_org_slug'] = org_slug
#             return self.get_response(request)
#
#         # Busca membership ativo
#         membership = OrganizationMember.objects.filter(
#             user=request.user, organization=org, is_active=True,
#         ).first()
#
#         if not membership:
#             messages.error(request, 'Você não tem acesso a esta organização.')
#             return redirect('post_login')  # ✅ NUNCA redirecionar pra /org/<slug>/...
#
#         # Tudo ok → injeta contexto
#         from core.services.context_service import ContextService
#         ctx = ContextService.build_member_context(request.user, org, membership)
#
#         request.tenant = org
#         request.user_role = membership.roles.order_by('-level').first()
#         request.context = ctx
#         request.session['last_org_slug'] = org_slug
#
#         return self.get_response(request)
#
# @dataclass
# class RequestContext:
#     organization: Optional[object] = None
#     membership: Optional[object] = None
#     professional: Optional[object] = None
#     client: Optional[object] = None
#     roles: Set[str] = field(default_factory=set)
#     modules: Set[str] = field(default_factory=set)
#     permissions: Set[str] = field(default_factory=set)
#     member_ctx: Optional[object] = None
import re

#from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from core.models import OrganizationModule, Permission
from core.services.context_service import ContextService, MemberContext
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
            return redirect('post_login')

        request.tenant = org
        request.context = self._build_context(request.user, org)
        request.session['last_org_slug'] = org_slug

        if not request.context:
            messages.error(request, 'Você não tem acesso a esta organização.')
            return redirect('post_login')

        if request.context.membership:
            request.user_role = request.context.membership.roles.order_by('-level').first()

        return self.get_response(request)

    def _get_org_slug(self, request):
        match = ORG_SLUG_PATTERN.match(request.path)
        return match.group('org_slug') if match else None

    def _build_context(self, user, org):
        if user.is_superuser:
            return MemberContext(
                user=user,
                organization=org,
                membership=None,
                roles={'superuser'},
                modules=set(
                    OrganizationModule.objects
                    .filter(organization=org, is_active=True)
                    .values_list('module__slug', flat=True)
                ),
                permissions=set(
                    Permission.objects.values_list('codename', flat=True)
                ),
            )

        membership = OrganizationMember.objects.filter(
            user=user, organization=org, is_active=True,
        ).first()
        if not membership:
            return None

        return ContextService.build_member_context(user, org, membership)
