# core/urls/tenant_url.py
from django.urls import path

from account.views.client_view import ClientListView
from account.views.member_view import MemberListView, MemberCreateView, MemberDetailView
from account.views.organization_view import OrganizationDetailView
from core.views.dashboard_view import DashboardView
from account.views.profile_view import ProfileView
from core.views.role_view import (
    RoleCreateView,
    RoleDetailView,
    RoleListView,
    RoleUpdateView,
)

app_name = 'tenant'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('clients/', ClientListView.as_view(), name='client_list'),

    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/create/', MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),

    #
    # # ── ORGANIZAÇÃO (detalhe único - a própria org do contexto) ──
    path('organization/detail', OrganizationDetailView.as_view(), name='organization_detail'),
    path('organization/update/', OrganizationDetailView.as_view(), name='organization_update'),

    # ── ROLES ──
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/permissions/', RoleUpdateView.as_view(), name='role_permissions_update'),
]
