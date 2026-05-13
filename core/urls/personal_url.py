# core/urls/personal_url.py
from django.urls import path

from core.views.personal.dashboard_view import PersonalDashboardView
from core.views.personal.profile_view import ProfileDetailView, ProfileEditView
from core.views.shared.space_select_view import SpaceSelectView

app_name = 'personal'

urlpatterns = [
    path('dashboard/', PersonalDashboardView.as_view(), name='dashboard'),
    path('space/select/personal/', SpaceSelectView.as_view(), {'kind': 'personal'}, name='space_select_personal',),
    path('perfil/', ProfileDetailView.as_view(), name='profile'),
    path('perfil/editar/', ProfileEditView.as_view(), name='profile_edit'),

]
