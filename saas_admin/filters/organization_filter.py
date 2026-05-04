
import django_filters

from account.models import Organization
from saas_admin.filters.base_filter import SaaSBaseFilter


class OrganizationFilter(SaaSBaseFilter):
    is_active = django_filters.BooleanFilter(label="Status de Ativação")

    class Meta:
        model = Organization
        fields = ['is_active']

        search_fields = ['company_name', 'slug']
