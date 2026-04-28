"""
URLs do app SaaS Admin.

Todas as rotas aqui ficam sob o prefixo /admin-saas/ (definido no
urls.py raiz do projeto) e são protegidas pelo SaaSAdminRequiredMixin.

Namespace: 'saas_admin'
Uso em templates: {% url 'saas_admin:dashboard' %}
"""

from django.urls import path

from saas_admin.views.dashboard import DashboardView
from saas_admin.views.organization import (
    OrganizationDetailView,
    OrganizationListView,
)

app_name = "saas_admin"

urlpatterns = [
    # Painel inicial → /admin-saas/
    path("", DashboardView.as_view(), name="dashboard",),

    # Organizações → /admin-saas/orgs/
    path("orgs/", OrganizationListView.as_view(), name="org_list",),

    # Detalhe de organização → /admin-saas/orgs/<id>/
    path("orgs/<int:pk>/", OrganizationDetailView.as_view(), name="org_detail",),
]
