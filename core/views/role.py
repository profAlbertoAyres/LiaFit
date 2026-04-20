# core/views/role.py
from core.views.base import BaseListView
from core.models import Role
from core.filters.role import RoleFilter  # O filtro que criamos anteriormente


class RoleListView(BaseListView):
    model = Role
    template_name = 'core/role/list.html'
    context_object_name = 'roles'

    # Exige a permissão técnica para ver papéis
    permission_required = 'core.view_role'

    filterset_class = RoleFilter
    paginate_by = 10
    ordering = 'level'  # Ordena pela hierarquia por padrão
