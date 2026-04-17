from django.urls import path
from account.views import OrganizationRegisterView, LoginView
from core.enums import account

app_name = 'auth' # Namespace isolado para auth

urlpatterns = [
    path('register/', OrganizationRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login')
    path('setup-password/<str:token>/', SetupPasswordView.as_view(), name='setup_password'),
]
