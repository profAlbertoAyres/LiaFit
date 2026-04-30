from django.urls import path

from account.forms.auth_form import LoginForm
from django.contrib.auth import views as auth_views

from account.views.organization_view import OrganizationRegisterView, RegisterSuccess, SetupPasswordView, \
    resend_password_view, ActivateOrganizationView, AcceptInviteView

app_name = 'auth' # Namespace isolado para auth

urlpatterns = [
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('register_success/', RegisterSuccess.as_view(), name='register_success'),
    path("activate-organization/<str:token>/", ActivateOrganizationView.as_view(), name="activate_organization",),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/auth/login.html', form_class=LoginForm,), name='login'),
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),
    path("resend-password/", resend_password_view, name="resend_password"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("accept-invite/<str:token>/", AcceptInviteView.as_view(), name="accept_invite",),

]
