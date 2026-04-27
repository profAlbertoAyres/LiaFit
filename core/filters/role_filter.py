# core/filters/role_view.py
import django_filters
from django.utils.translation import gettext_lazy as _
from core.filters.base_filter import BaseFilter
from core.models import Role, RolePermission

class RoleFilter(BaseFilter):
    class Meta:
        model = Role
        fields = []
        search_fields = ['name', 'slug', 'description']

class RolePermissionFilter(BaseFilter):
    role = django_filters.ModelChoiceFilter(
        queryset=Role.objects.none(),
        label=_("Cargo"),
        empty_label=_("Todos os Cargos")
    )

    class Meta:
        model = RolePermission
        fields = ['role']
        search_fields = ['role__name', 'permission__name']

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, request=request, **kwargs)
        if self.organization:
            self.form.fields['role'].queryset = Role.objects.filter(
                organization=self.organization
            )
