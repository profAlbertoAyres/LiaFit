"""
URLs do app SaaS Admin.

Todas as rotas aqui ficam sob o prefixo /painel/ (definido no
urls.py raiz do projeto) e são protegidas pelo SaaSAdminRequiredMixin.

Namespace: 'saas_admin'
Uso em templates: {% url 'saas_admin:dashboard' %}
"""

from django.urls import path

from account.views.organization_view import OrganizationDetailView
from core.views.master_view import ModuleListView, ModuleCreateView, PermissionListView, PermissionCreateView
from core.views.shared.space_select_view import SpaceSelectView
from saas_admin.views.dashboard_view import DashboardView
from saas_admin.views.organization_views import OrganizationListView, OrganizationCreateView, \
    OrganizationToggleStatusView
from saas_admin.views.specialty_view import SpecialtyListView, SpecialtyCreateView, SpecialtyUpdateView

app_name = "saas_admin"

urlpatterns = [
    # Painel inicial → /admin-saas/
    path("", DashboardView.as_view(), name="dashboard"),
    path('space/select/saas/', SpaceSelectView.as_view(), {'kind': 'saas'}, name='space_select_saas',),

    # Organizações → /admin-saas/orgs/
    path("organizations/", OrganizationListView.as_view(), name="organization_list",),
    path("organizations/new/", OrganizationCreateView.as_view(), name="organization_create",),

    path("organizations/<int:pk>/", OrganizationDetailView.as_view(), name="organization_detail"),
    path("organizations/<int:pk>/toggle-status/", OrganizationToggleStatusView.as_view(),
         name="organization_toggle_status"),


    #specialty
    path("specialties/", SpecialtyListView.as_view(), name="specialty_list",),
    path("specialties/create/", SpecialtyCreateView.as_view(), name="specialty_create",),
    path("specialties/<int:pk>/edit/", SpecialtyUpdateView.as_view(), name="specialty_update",
    ),

    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/create/', ModuleCreateView.as_view(), name='module_create'),

    # ── PERMISSÕES GLOBAIS ──
    path('permissions/', PermissionListView.as_view(), name='permission_list'),
    path('permissions/create/', PermissionCreateView.as_view(), name='permission_create'),
]
