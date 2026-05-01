from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from account.services.onboarding_service import OnboardingService
from core.forms.base_form import BaseForm

User = get_user_model()


class OrganizationRegistrationForm(BaseForm):
    company_name = forms.CharField(
        label=_("Nome da Empresa (Clínica/Estúdio/Academia)"),
        max_length=255,
    )
    fullname = forms.CharField(label=_("Nome completo"), max_length=150)
    email = forms.EmailField(label=_("E-mail"), max_length=150)

    # Hidden: marcado como True quando o usuário confirma no modal
    confirm_existing = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput(),
    )

    email_already_exists = False
    existing_user_needs_password = False

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        confirm = cleaned.get("confirm_existing")

        if not email:
            return cleaned

        info = OnboardingService.check_email_exists(email)

        if info["is_disabled"]:
            raise forms.ValidationError(
                _("Esta conta está desativada. Entre em contato com o suporte.")
            )

        if info["exists"] and not confirm:
            self.email_already_exists = True
            self.existing_user_needs_password = info["needs_password"]
            self._existing_user = info["user"]
            return cleaned

        # Se existe E confirmou → guarda o user pra usar no save()
        if info["exists"] and confirm:
            self._existing_user = info["user"]

        return cleaned

    def save(self, request=None):
        # Fluxo multi-empresa: usuário existente confirmou
        if self.cleaned_data.get("confirm_existing") and getattr(self, "_existing_user", None):
            org_data = {"company_name": self.cleaned_data["company_name"]}
            return OnboardingService.register_organization_for_existing_user(
                user=self._existing_user,
                organization_data=org_data,
                request=request,
            )

        # Fluxo padrão: usuário novo
        user_data = {
            "fullname": self.cleaned_data["fullname"],
            "email": self.cleaned_data["email"],
        }
        org_data = {"company_name": self.cleaned_data["company_name"]}
        return OnboardingService.register_organization(
            user_data, org_data, request=request
        )


class SetupPasswordForm(BaseForm):

    password1 = forms.CharField(
        label=_("Nova senha"),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Confirmação da senha"),
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        pw1 = cleaned_data.get("password1")
        pw2 = cleaned_data.get("password2")

        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError(_("As senhas não conferem."))

        if pw1:
            validate_password(pw1)

        return cleaned_data

    def save(self, token, request=None):
        return OnboardingService.setup_password(
            token_str=token,
            password=self.cleaned_data["password1"],
            request=request,
        )

class AcceptInviteForm(SetupPasswordForm):

    def save(self, token, request=None):
        return OnboardingService.activate_member(
            token_str=token,
            password=self.cleaned_data["password1"],
            request=request,
        )

class PasswordResetConfirmForm(SetupPasswordForm):

    def save(self, token, request=None):
        return OnboardingService.confirm_password_reset(
            token_str=token,
            password=self.cleaned_data["password1"],
            request=request,
        )

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.EmailInput(attrs={
            "autocomplete": "email",
            "placeholder": "seu@email.com",
            "class": "form-control",
        }),
        error_messages={
            "required": "Informe seu e-mail.",
            "invalid": "E-mail inválido.",
        },
    )

    def get_normalized_email(self):
        return self.cleaned_data["email"].strip().lower()
