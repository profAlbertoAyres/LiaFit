from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

from account.models import Organization
from account.services.onboarding_service import OnboardingService
from saas_admin.filters.organization_filter import OrganizationFilter
from saas_admin.forms.AdminOrganizationCreateForm import AdminOrganizationCreateForm
from saas_admin.views.base_view import SaaSBaseListView, SaaSBaseFormView


class OrganizationListView(SaaSBaseListView):
    model = Organization
    template_name = "saas_admin/organization/list.html"
    context_object_name = "organizations"
    filterset_class = OrganizationFilter


    def get_queryset(self):

        return super().get_queryset()

class OrganizationCreateView(SaaSBaseFormView):
    form_class = AdminOrganizationCreateForm
    template_name = "saas_admin/organization/create.html"
    success_url = reverse_lazy("saas_admin:organization_list")

    def form_valid(self, form):
        OnboardingService.register_organization(
            user_data=form.get_user_data(),
            organization_data=form.get_organization_data(),
            request=self.request,
        )
        messages.success(self.request, "Organização criada com sucesso. E-mail de ativação enviado.")
        return redirect(self.success_url)
