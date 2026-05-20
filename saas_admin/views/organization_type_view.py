from django.urls import reverse_lazy

from account.models.organization import OrganizationType
from saas_admin.filters.organization_type_filter import OrganizationTypeFilter
from saas_admin.forms.organization_type_form import OrganizationTypeForm
from saas_admin.views.base_view import SaaSBaseListView, SaaSBaseCreateView, SaaSBaseUpdateView


class OrganizationTypeListView(SaaSBaseListView):
    model = OrganizationType
    filterset_class = OrganizationTypeFilter
    template_name = "saas_admin/organization_type/list.html"
    context_object_name = "organization_types"

class OrganizationTypeCreateView(SaaSBaseCreateView):
    model = OrganizationType
    form_class = OrganizationTypeForm
    template_name = "saas_admin/organization_type/create.html"
    success_url = reverse_lazy("saas_admin:organization_type_list")

class OrganizationTypeUpdateView(SaaSBaseUpdateView):
    model = OrganizationType
    form_class = OrganizationTypeForm
    template_name = "saas_admin/organization_type/create.html"
    success_url = reverse_lazy("saas_admin:organization_type_list")