from catalog.models.service_type import ServiceType
from saas_admin.forms.base_form import SaaSBaseModelForm


class ServiceTypeForm(SaaSBaseModelForm):
    class Meta:
        model = ServiceType
        fields = ['name', 'description', 'is_active']
