# core/filters/master.py
import django_filters
from core.filters.base import BaseFilter
from core.models import Module, Permission, Role


class ModuleFilter(BaseFilter):
    class Meta:
        model = Module
        fields = ['is_active']  # Exemplo: Dropdown para filtrar ativos/inativos
        search_fields = ['name', 'slug', 'description']  # Onde a barra de busca vai procurar


class PermissionFilter(BaseFilter):
    module = django_filters.ModelChoiceFilter(
        queryset=Module.objects.all(),
        label="Módulo",
        empty_label="Todos os Módulos"
    )

    class Meta:
        model = Permission
        fields = ['module']
        search_fields = ['name', 'codename', 'description']


class RoleFilter(BaseFilter):
    class Meta:
        model = Role
        fields = []
        search_fields = ['name', 'slug', 'description']
