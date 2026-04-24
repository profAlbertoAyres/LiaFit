from collections import defaultdict

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from core.filters.role import RoleFilter
from core.forms.role import RoleForm, RolePermissionForm
from core.models import Role, Permission
from core.services.role_service import RoleService
from core.views.base import (
    BaseCreateView,
    BaseDetailView,
    BaseListView,
    BaseUpdateView,
)


class RoleListView(BaseListView):
    model = Role
    template_name = 'core/role/list.html'
    context_object_name = 'roles'
    permission_required = 'account.view_role'
    filterset_class = RoleFilter
    paginate_by = 10
    ordering = 'level'

    def get_queryset(self):
        qs = super().get_queryset()
        membership = self.get_membership()

        return RoleService.filter_visible_roles(self.request, qs, membership)


class RoleDetailView(BaseDetailView):
    model = Role
    template_name = 'core/role/detail.html'
    context_object_name = 'role'
    permission_required = 'account.view_role'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        membership = self.get_membership()
        RoleService.check_hierarchy_permission(self.request, obj, membership)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(RoleService.get_role_context_flags(self.request, self.object))

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        selected_permission_ids = self.request.POST.getlist('permissions')
        membership = self.get_membership()

        try:
            # 👇 O Service resolve TUDO!
            permissions_updated = RoleService.process_role_permissions_update(
                request=self.request,
                role=self.object,
                membership=membership,
                selected_permission_ids=selected_permission_ids
            )

            if permissions_updated:
                messages.success(self.request, 'Permissões atualizadas com sucesso!')
            else:
                messages.warning(self.request, 'Você não possui privilégios para alterar as permissões deste cargo.')

        except PermissionDenied as e:
            messages.error(self.request, str(e))

        # Dica: redirect para a mesma página para o usuário ver o que salvou!
        return redirect('tenant:role_detail', org_slug=self.request.context.organization.slug, pk=self.object.pk)

class RoleCreateView(BaseCreateView):
    model = Role
    form_class = RoleForm
    template_name = 'core/role/create.html'
    permission_required = 'account.add_role'

    def get_success_url(self):
        tenant = self.get_tenant()
        return reverse('tenant:role_list', kwargs={'org_slug': tenant.slug})


class RoleUpdateView(BaseUpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'core/role/create.html'
    context_object_name = 'role'
    permission_required = 'change_configuracoes_role'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        membership = self.get_membership()
        RoleService.check_hierarchy_permission(self.request, obj, membership)

        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Papel atualizado com sucesso.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'tenant:role_detail',
            kwargs={
                'org_slug': self.request.context.organization.slug,
                'pk': self.object.pk,
            }
        )


