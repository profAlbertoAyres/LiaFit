from account.models.organization import OrganizationType
from saas_admin.forms.base_form import SaaSBaseModelForm


class OrganizationTypeForm(SaaSBaseModelForm):
    class Meta:
        model = OrganizationType
        fields = ['name', 'description', 'is_active']
