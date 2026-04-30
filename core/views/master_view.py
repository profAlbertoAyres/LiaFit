from django.urls import reverse_lazy

from core.forms.master_form import ModuleForm, PermissionForm, RoleForm
from core.models import Module, Permission, Role
from core.views import BaseListView, BaseCreateView


class ModuleListView(BaseListView):
    model = Module
    template_name = 'core/module_list.html'
    require_tenant = False
    # permission_required = 'master_view_module' # Opcional: permissão de superadmin

class ModuleCreateView(BaseCreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'core/module_form.html'
    require_tenant = False
    success_url = reverse_lazy('module_list')

# ... (UpdateView e DeleteView para Module seguem o mesmo padrão) ...


class PermissionListView(BaseListView):
    model = Permission
    template_name = 'core/permission_list.html'
    require_tenant = False

class PermissionCreateView(BaseCreateView):
    model = Permission
    form_class = PermissionForm
    template_name = 'core/permission_form.html'
    require_tenant = False
    success_url = reverse_lazy('permission_list')


class RoleListView(BaseListView):
    model = Role
    template_name = 'core/role_list.html'
    require_tenant = False

class RoleCreateView(BaseCreateView):
    model = Role
    form_class = RoleForm
    template_name = 'core/role_form.html'
    require_tenant = False
    success_url = reverse_lazy('role_list')
