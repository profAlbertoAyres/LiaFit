
from core.models.role_permission import RolePermission
from core.views import BaseListView, BaseCreateView


class RolePermissionListView(BaseListView):
    model = RolePermission
    template_name = 'core/tenant_role_permission_list.html'
    # require_tenant = True (Já é True na sua classe BaseAuthMixin)
    permission_required = 'settings.view_role'  # Permissão que o Tenant precisa ter

