# core/urls/master.py
from django.urls import path

from core.views import DashboardView
from core.views.master import (
    ModuleListView, ModuleCreateView,
    PermissionListView, PermissionCreateView,
    RoleListView, RoleCreateView
)

app_name = 'core'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # ── MÓDULOS ──
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/create/', ModuleCreateView.as_view(), name='module_create'),

    # ── PERMISSÕES GLOBAIS ──
    path('permissions/', PermissionListView.as_view(), name='permission_list'),
    path('permissions/create/', PermissionCreateView.as_view(), name='permission_create'),

    # ── CARGOS BASE (ROLES) ──
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
]
