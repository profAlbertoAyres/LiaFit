import django_filters

from account.models.organization import OrganizationType
from saas_admin.filters.base_filter import SaaSBaseFilter


class OrganizationTypeFilter(SaaSBaseFilter):
    is_active = django_filters.BooleanFilter(label="Status de Ativação")

    class Meta:
        model = OrganizationType
        fields = ['is_active']

        search_fields = ['name', 'description']
