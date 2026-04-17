from django.contrib.auth import get_user_model
from django import forms

from account.services.onboarding_service import OnboardingService
from core.forms import BaseForm

User = get_user_model()

class OrganizationRegistrationForm(BaseForm):
    company_name = forms.CharField(label="Nome da Empresa (Clínica/Estúdio)", max_length=255)
    fullname = forms.CharField(label='Nome completo', max_length=150)
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    def save(self):
        user_data = {
            'fullname': self.cleaned_data['fullname'],
            'email': self.cleaned_data['email'],
        }
        org_data = {
            'company_name': self.cleaned_data['company_name'], # <--- MAPEADO AQUI!
            'slug': self.cleaned_data['company_name']  # <--- MAPEADO AQUI!
        }

        return OnboardingService.register_organization(user_data, org_data)

