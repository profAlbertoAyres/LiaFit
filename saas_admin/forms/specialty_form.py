from account.models import Specialty
from saas_admin.forms.base_form import SaaSBaseModelForm


class SpecialtyForm(SaaSBaseModelForm):
    class Meta:
        model = Specialty
        fields = ['name', 'description', 'is_active']
