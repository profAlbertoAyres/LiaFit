import django_filters

from account.models import Specialty
from saas_admin.filters.base_filter import SaaSBaseFilter


class SpecialtyFilter(SaaSBaseFilter):
    is_active = django_filters.BooleanFilter(label="Status de Ativação")

    class Meta:
        model = Specialty
        fields = ['is_active']

        search_fields = ['name', 'description']
