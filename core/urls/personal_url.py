# core/urls/personal_url.py
from django.urls import path

from core.views.master_view import (
    ModuleListView, ModuleCreateView,
    PermissionListView, PermissionCreateView,)
from core.views.personal.dashboard_view import PersonalDashboardView

app_name = 'personal'

urlpatterns = [
    path('dashboard/', PersonalDashboardView.as_view(), name='dashboard'),

    # ── MÓDULOS ──

    ]
