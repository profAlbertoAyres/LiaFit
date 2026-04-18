from django.urls import path

from account import views
from account.forms import LoginForm
from account.views import OrganizationRegisterView, SetupPasswordView, RegisterSuccess
from django.contrib.auth import views as auth_views

app_name = 'auth' # Namespace isolado para auth

urlpatterns = [
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('register_success/', RegisterSuccess.as_view(), name='register_success'),
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/auth/login.html',
        form_class=LoginForm,
    ), name='login'),
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),
    path("resend-password/", views.resend_password_view, name="resend_password"),

]
