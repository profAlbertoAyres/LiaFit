from django.urls import path
from core.views import DashboardView
from core.views.role import (
    RoleDetailView,
    RoleUpdateView,
    RoleListView,
    RoleCreateView,
)
from core.views.tenant import (
    RolePermissionListView,
    RolePermissionCreateView,
    UserPermissionListView,
    UserPermissionCreateView,
)

app_name = 'tenant'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # ── PERMISSÕES DO CARGO (Personalização da Clínica) ──
    path('role-permissions/', RolePermissionListView.as_view(), name='role_permission_list'),
    path('role-permissions/create/', RolePermissionCreateView.as_view(), name='role_permission_create'),

    # ── PERMISSÕES DO USUÁRIO (Exceções para o Dr. João) ──
    path('user-permissions/', UserPermissionListView.as_view(), name='user_permission_list'),
    path('user-permissions/create/', UserPermissionCreateView.as_view(), name='user_permission_create'),

    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/update/', RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/permissions/', RoleCreateView.as_view(), name='role_permissions_update'),
]
