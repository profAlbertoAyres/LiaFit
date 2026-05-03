from django.contrib.auth import views as auth_views
from django.urls import path

from account.forms.auth_form import LoginForm
from account.views.auth_view import CustomLoginView
from account.views.client_view import AcceptClientInviteView
from account.views.organization_view import (
    AcceptInviteView,
    ActivateOrganizationView,
    OrganizationRegisterView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterSuccess,
    SetupPasswordView,
)

app_name = 'auth'  # Namespace isolado para auth

urlpatterns = [
    # Registro
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('register_success/', RegisterSuccess.as_view(), name='register_success'),

    # Login / Logout
    path('login/', CustomLoginView.as_view(), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Ativação inicial (definir senha pela 1ª vez)
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),

    # Ativação de empresa adicional (usuário já tem senha)
    path('activate-organization/<str:token>/', ActivateOrganizationView.as_view(), name='activate_organization'),
    path('accept-client-invite/<uuid:token>/', AcceptClientInviteView.as_view(), name='accept_client_invite'),


    # Convite de membro
    path('accept-invite/<str:token>/', AcceptInviteView.as_view(), name='accept_invite'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
