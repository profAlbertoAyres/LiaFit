import django_filters

from catalog.models.service_type import ServiceType
from saas_admin.filters.base_filter import SaaSBaseFilter


class ServiceTypeFilter(SaaSBaseFilter):
    is_active = django_filters.BooleanFilter(label="Status de Ativação")

    class Meta:
        model = ServiceType
        fields = ['is_active']

        search_fields = ['name', 'description']
