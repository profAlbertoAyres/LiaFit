# account/views/member_view.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.views.generic import FormView

from account.filters.member_filter import OrganizationMemberFilter
from account.forms.member_form import MemberCreateForm
from account.models import OrganizationMember
from account.services.member_service import MemberService
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
    ordering = 'user__fullname'

    def get_queryset(self):
        return super().get_queryset().select_related('user').prefetch_related('roles')


class MemberDetailView(BaseDetailView):
    model = OrganizationMember
    template_name = "accounts/member/detail.html"
    context_object_name = "member"

    require_tenant = True
    permission_required = "settings.view_member"


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

