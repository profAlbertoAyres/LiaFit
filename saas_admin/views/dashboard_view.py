"""
View do Dashboard inicial do SaaS Admin.

Renderiza /painel/ com métricas globais da plataforma.
Protegida por SaaSAdminRequiredMixin (só equipe interna acessa).

A view é fina propositalmente: toda a lógica de agregação
mora em SaaSAdminDashboardService.
"""
from django.views.generic import TemplateView

from saas_admin.services.dashboard_service import SaaSAdminDashboardService
from saas_admin.views.base_view import SaaSAdminRequiredMixin


class DashboardView(SaaSAdminRequiredMixin, TemplateView):
    """Dashboard inicial do painel SaaS Admin."""

    template_name = "saas_admin/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["metrics"] = SaaSAdminDashboardService.get_metrics()
        context["page_title"] = "Painel SaaS Admin"
        return context
