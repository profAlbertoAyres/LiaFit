from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from account.services.onboarding_service import OnboardingService
from core.forms.base import BaseForm, LiaFitStyleMixin

User = get_user_model()

class OrganizationRegistrationForm(BaseForm):
    company_name = forms.CharField(label=_("Nome da Empresa (Clínica/Estúdio/Acadêmia)"), max_length=255)
    fullname = forms.CharField(label=_('Nome completo'), max_length=150)
    email = forms.EmailField(label=_('E-mail'),max_length=150)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    def save(self, request=None):
        user_data = {
            'fullname': self.cleaned_data['fullname'],
            'email': self.cleaned_data['email'],
        }
        org_data = {
            'company_name': self.cleaned_data['company_name'],
        }

        return OnboardingService.register_organization(user_data, org_data, request=request)


class SetupPasswordForm(BaseForm):
    password1 = forms.CharField(label=_("Nova senha"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirmação da senha"), widget=forms.PasswordInput)

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


class LoginForm(LiaFitStyleMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields['username'].widget.input_type = 'email'
            self.fields['username'].label = _('E-mail')
            self.fields['username'].widget.attrs['autocomplete'] = 'email'

        # Ajusta o campo de senha
        if 'password' in self.fields:
            self.fields['password'].label = _("Senha")

        # Aplica toda a mágica do seu Mixin (lia-form-control, placeholders, etc.)
        self._apply_liafit_styles()


