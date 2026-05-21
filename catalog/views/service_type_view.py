from django.urls import reverse_lazy

from catalog.models import ServiceType
from catalog.filters.service_type_filter import ServiceTypeFilter
from catalog.forms.service_type_form import ServiceTypeForm
from saas_admin.views.base_view import SaaSBaseListView, SaaSBaseCreateView, SaaSBaseUpdateView


class ServiceTypeListView(SaaSBaseListView):
    model = ServiceType
    filterset_class = ServiceTypeFilter
    template_name = "catalog/service_type/list.html"
    context_object_name = "service_types"


class ServiceTypeCreateView(SaaSBaseCreateView):
    model = ServiceType
    form_class = ServiceTypeForm
    template_name = "catalog/service_type/create.html"
    success_url = reverse_lazy("catalog:service_type_list")


class ServiceTypeUpdateView(SaaSBaseUpdateView):
    model = ServiceType
    form_class = ServiceTypeForm
    template_name = "catalog/service_type/create.html"
    success_url = reverse_lazy("catalog:service_type_list")
