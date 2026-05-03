# core/urls/tenant_url.py
from django.urls import path

from account.views.client_view import ClientListView, ClientCreateView, ClientDetailView, ClientUpdateView, \
    ClientArchiveView
from account.views.organization_view import OrganizationDetailView
from core.views.dashboard_view import DashboardView
from account.views.profile_view import ProfileView
from account.views.member_view import (
    MemberListView,
    MemberCreateView,
    MemberDetailView,
    MemberUpdateView,
    MemberRoleAssignView,
    MemberRoleRevokeView,
    MemberRoleUndoView,
)

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
    path('members/', MemberListView.as_view(), name='member_list'),
    path('members/create/', MemberCreateView.as_view(), name='member_create'),
    path('members/<int:pk>/', MemberDetailView.as_view(), name='member_detail'),
    path('members/<int:pk>/update/', MemberUpdateView.as_view(), name='member_update'),

    # 🆕 Role assignment HTMX
    path('members/<int:pk>/roles/<int:role_id>/assign/', MemberRoleAssignView.as_view(), name='member_role_assign'),
    path('members/<int:pk>/roles/<int:role_id>/revoke/', MemberRoleRevokeView.as_view(), name='member_role_revoke'),
    path('members/roles/log/<int:log_id>/undo/', MemberRoleUndoView.as_view(), name='member_role_undo'),

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


    path('client/', ClientListView.as_view(), name='client_list'),
    path('client/new/', ClientCreateView.as_view(), name='client_create'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('client/<int:pk>/edit/', ClientUpdateView.as_view(), name='client_update'),
    path('client/<int:pk>/archive/', ClientArchiveView.as_view(), name='client_archive'),
]
