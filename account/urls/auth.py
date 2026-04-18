from django.urls import path

from account import views
from account.views import OrganizationRegisterView, SetupPasswordView
from django.contrib.auth import views as auth_views

app_name = 'auth' # Namespace isolado para auth

urlpatterns = [
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/auth/login.html'), name='login'),
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),
    path("resend-password/", views.resend_password_view, name="resend_password"),

]
