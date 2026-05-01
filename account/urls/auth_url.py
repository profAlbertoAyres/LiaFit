from django.contrib.auth import views as auth_views
from django.urls import path

from account.forms.auth_form import LoginForm
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
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/auth/login.html',
            form_class=LoginForm,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Ativação inicial (definir senha pela 1ª vez)
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),

    # Ativação de empresa adicional (usuário já tem senha)
    path('activate-organization/<str:token>/', ActivateOrganizationView.as_view(), name='activate_organization'),

    # Convite de membro
    path('accept-invite/<str:token>/', AcceptInviteView.as_view(), name='accept_invite'),

    # 🆕 Reset de senha
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
