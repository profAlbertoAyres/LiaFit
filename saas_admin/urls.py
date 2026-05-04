"""
URLs do app SaaS Admin.

Todas as rotas aqui ficam sob o prefixo /painel/ (definido no
urls.py raiz do projeto) e são protegidas pelo SaaSAdminRequiredMixin.

Namespace: 'saas_admin'
Uso em templates: {% url 'saas_admin:dashboard' %}
"""

from django.urls import path

from saas_admin.views.organization_views import OrganizationListView, OrganizationCreateView
from saas_admin.views.specialty_view import SpecialtyListView, SpecialtyCreateView, SpecialtyUpdateView

app_name = "saas_admin"

urlpatterns = [
    # Painel inicial → /admin-saas/
    # path("", DashboardView.as_view(), name="dashboard",),

    # Organizações → /admin-saas/orgs/
    path("organizations/", OrganizationListView.as_view(), name="organization_list",),
    path("organizations/new/", OrganizationCreateView.as_view(), name="organization_create",),

    # Detalhe de organização → /admin-saas/orgs/<id>/
    # path("orgs/<int:pk>/", OrganizationDetailView.as_view(), name="organization_detail",),


    #specialty
    path("specialties/", SpecialtyListView.as_view(), name="specialty_list",),
    path("specialties/create/", SpecialtyCreateView.as_view(), name="specialty_create",),
    path("specialties/<int:pk>/edit/", SpecialtyUpdateView.as_view(), name="specialty_update",
    ),
]
