from django.urls import reverse_lazy

from account.models import Specialty
from saas_admin.filters.specialty_filter import SpecialtyFilter
from saas_admin.forms.specialty_form import SpecialtyForm
from saas_admin.views.base_view import SaaSBaseListView, SaaSBaseCreateView, SaaSBaseUpdateView


class SpecialtyListView(SaaSBaseListView):
    model = Specialty
    filterset_class = SpecialtyFilter
    template_name = "saas_admin/specialty/list.html"
    context_object_name = "specialties"

class SpecialtyCreateView(SaaSBaseCreateView):
    model = Specialty
    form_class = SpecialtyForm
    template_name = "saas_admin/specialty/create.html"
    success_url = reverse_lazy("saas_admin:specialty_list")

class SpecialtyUpdateView(SaaSBaseUpdateView):
    model = Specialty
    form_class = SpecialtyForm
    template_name = "saas_admin/specialty/create.html"
    success_url = reverse_lazy("saas_admin:specialty_list")