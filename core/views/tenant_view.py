from django.urls import reverse_lazy

from core.forms import UserPermissionForm, RolePermissionForm
from core.models.role_permission import RolePermission
from core.models.user_permission import UserPermission
from core.views import BaseListView, BaseCreateView


class RolePermissionListView(BaseListView):
    model = RolePermission
    template_name = 'core/tenant_role_permission_list.html'
    # require_tenant = True (Já é True na sua classe BaseAuthMixin)
    permission_required = 'settings.view_role'  # Permissão que o Tenant precisa ter


class RolePermissionCreateView(BaseCreateView):
    model = RolePermission
    form_class = RolePermissionForm
    template_name = 'core/tenant_role_permission_form.html'
    permission_required = 'settings.change_role'
    success_url = reverse_lazy('tenant_role_permission_list')

    # O seu BaseCreateView.form_valid() já vai injetar automaticamente a
    # organization no objeto antes de salvar!


class UserPermissionListView(BaseListView):
    model = UserPermission
    template_name = 'core/tenant_user_permission_list.html'
    # 🩹 era 'settings.view_user_permission' (codename inexistente no catálogo).
    # UserPermission é override sobre Member → reusa permissão do item Member.
    permission_required = 'settings.view_member'


class UserPermissionCreateView(BaseCreateView):
    model = UserPermission
    form_class = UserPermissionForm
    template_name = 'core/tenant_user_permission_form.html'
    # 🩹 era 'settings.change_user_permission' (codename inexistente no catálogo).
    permission_required = 'settings.change_member'
    success_url = reverse_lazy('tenant_user_permission_list')

    def get_form_kwargs(self):
        return super().get_form_kwargs()
