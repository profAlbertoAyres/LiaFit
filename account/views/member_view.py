# account/views/member_views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.views import View

from account.exceptions import RoleAssignmentError
from account.filters.member_filter import OrganizationMemberFilter
from account.forms.member_form import MemberCreateForm
from account.models import OrganizationMember
from account.services.member_service import MemberService
from core.models import Role, RoleAssignmentLog
from core.services.role_assignment_service import RoleAssignmentService
from core.services.role_service import RoleService
from core.views.base_view import (
    BaseListView,
    BaseDetailView,
    BaseUpdateView, BaseFormView,
)


class MemberListView(BaseListView):
    model = OrganizationMember
    template_name = "accounts/member/list.html"
    context_object_name = "members"
    require_tenant = True
    permission_required = "settings.view_member"

    paginate_by = 10
    filterset_class = OrganizationMemberFilter

    def get_queryset(self):
        return super().get_queryset().select_related('user').prefetch_related('roles')


class MemberDetailView(BaseDetailView):
    model = OrganizationMember
    template_name = "accounts/member/detail.html"
    context_object_name = "member"

    require_tenant = True
    permission_required = "settings.view_member"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tenant = self.request.context.organization
        actor_membership = self.request.context.membership

        visible_roles = RoleService.filter_visible_roles(
            self.request,
            Role.objects.filter(organization=tenant, is_active=True),
            actor_membership,
        ).order_by("level")

        assigned_ids = set(self.object.roles.values_list("pk", flat=True))
        for role in visible_roles:
            role.is_assigned = role.pk in assigned_ids

        context["available_roles"] = visible_roles
        return context


class MemberCreateView(BaseFormView):
    form_class = MemberCreateForm
    template_name = "accounts/member/create.html"
    permission_required = "settings.add_member"

    def form_valid(self, form):
        membership = MemberService.create_member(
            organization=self.request.context.organization,
            data=form.cleaned_data,
            request=self.request,
        )

        messages.success(
            self.request,
            f"Membro cadastrado! E-mail enviado para {membership.user.email}.",
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'tenant:member_list',
            kwargs={'org_slug': self.request.context.organization.slug},
        )

class MemberUpdateView(BaseUpdateView):
    model = OrganizationMember
    form_class =MemberCreateForm
    template_name = "accounts/member/create.html"

    require_tenant = True
    permission_required = "settings.change_member"

    def get_success_url(self):
        messages.success(self.request, "Membro atualizado com sucesso!")
        return reverse('tenant:member_list', kwargs={'org_slug': self.request.context.organization.slug})


# ──────────────── HTMX: Role Assignment (standalone) ────────────────

class _RoleHTMXBase(LoginRequiredMixin, View):
    """
    Base local para as views HTMX de role assignment.
    Não depende de BaseAuthMixin/TenantContextMixin.
    Faz checagem manual de tenant + permissão usando request.context.
    """
    http_method_names = ["post"]
    permission_required = "settings.change_member"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        ctx = getattr(request, "context", None)
        if not ctx or not getattr(ctx, "organization", None):
            messages.error(request, "Organização não encontrada.")
            return redirect("master:dashboard")

        if not request.user.is_superuser:
            if not getattr(ctx, "membership", None):
                messages.error(request, "Acesso negado.")
                return redirect("master:dashboard")
            if not ctx.has_permission(self.permission_required):
                messages.error(request, "Você não tem permissão para esta ação.")
                return redirect("master:dashboard")

        self.tenant = ctx.organization
        self.actor_membership = ctx.membership
        return super().dispatch(request, *args, **kwargs)


class MemberRoleAssignView(_RoleHTMXBase):
    def post(self, request, pk, role_id, *args, **kwargs):
        membership = get_object_or_404(OrganizationMember, pk=pk, organization=self.tenant)
        role = get_object_or_404(Role, pk=role_id, organization=self.tenant)

        try:
            log = RoleAssignmentService.assign(
                membership=membership,
                role=role,
                actor=request.user,
                actor_membership=self.actor_membership,
            )
        except RoleAssignmentError as e:
            return _render_role_error(request, str(e))

        return _render_role_card(request, membership, role, log=log)


class MemberRoleRevokeView(_RoleHTMXBase):
    def post(self, request, pk, role_id, *args, **kwargs):
        membership = get_object_or_404(OrganizationMember, pk=pk, organization=self.tenant)
        role = get_object_or_404(Role, pk=role_id, organization=self.tenant)

        try:
            log = RoleAssignmentService.revoke(
                membership=membership,
                role=role,
                actor=request.user,
                actor_membership=self.actor_membership,
            )
        except RoleAssignmentError as e:
            return _render_role_error(request, str(e))

        return _render_role_card(request, membership, role, log=log)


class MemberRoleUndoView(_RoleHTMXBase):
    def post(self, request, log_id, *args, **kwargs):
        log = get_object_or_404(RoleAssignmentLog, pk=log_id, organization=self.tenant)

        try:
            RoleAssignmentService.undo(
                log=log,
                actor=request.user,
                actor_membership=self.actor_membership,
            )
        except RoleAssignmentError as e:
            return _render_role_error(request, str(e))

        return _render_role_card(request, log.membership, log.role, log=None)


# ──────────────── HELPERS ────────────────

def _render_role_card(request, membership, role, *, log):
    is_assigned = membership.roles.filter(pk=role.pk).exists()
    return render(
        request,
        "accounts/member/_role_toggle_card.html",
        {
            "membership": membership,
            "role": role,
            "is_assigned": is_assigned,
            "last_log": log,
        },
    )


def _render_role_error(request, message):
    response = render(
        request,
        "accounts/member/_role_error.html",
        {"message": message},
        status=422,
    )
    response["HX-Reswap"] = "none"
    return response
