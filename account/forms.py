from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

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


class SetupPasswordForm(BaseForm):
    password1 = forms.CharField(label="Nova senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmação da senha", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("As senhas não conferem.")

        if pw1:
            validate_password(pw1)

        return cleaned_data

    def save(self, token, request=None):
        return OnboardingService.setup_password(
            token_str=token,
            password=self.cleaned_data["password1"],
            request=request,
        )


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({'class': 'lia-form-control'})
        self.fields['password'].widget.attrs.update({'class': 'lia-form-control'})


