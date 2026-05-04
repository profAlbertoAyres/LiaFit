from django import forms

from core.constants.locations import BRAZILIAN_STATES_BY_NAME
from saas_admin.forms.base_form import SaaSBaseForm

class AdminOrganizationCreateForm(SaaSBaseForm):
    # ─── DADOS DO RESPONSÁVEL (USUÁRIO) ───
    user_fullname = forms.CharField(
        label="Nome Completo do Responsável",
        max_length=255,
        required=True,
        help_text="Nome do dono da conta (opcional se o e-mail já existir)."
    )
    user_email = forms.EmailField(
        label="E-mail do Responsável (Login)",
        required=True,
        help_text="Será usado para login. Se já existir no sistema, a empresa será vinculada a ele."
    )

    # ─── DADOS DA EMPRESA (ORGANIZAÇÃO) ───
    company_name = forms.CharField(
        label="Nome da Empresa / Razão Social",
        max_length=255,
        required=True
    )
    company_document = forms.CharField(
        label="CNPJ / CPF",
        max_length=50,
        required=False
    )
    company_email = forms.EmailField(
        label="E-mail de Contato da Empresa",
        required=False,
        help_text="E-mail público ou de atendimento da empresa (diferente do login)."
    )
    company_phone = forms.CharField(
        label="Telefone da Empresa",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'data-mask': 'phone'}),

    )

    # ============================================================
    # 3. ORGANIZAÇÃO — Endereço (opcional)
    # ============================================================
    zip_code = forms.CharField(
        label='CEP',
        max_length=9,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': '00000-000',
            'data-mask': 'cep',
        }),
    )
    address = forms.CharField(
        label='Endereço',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Rua',
        }),
    )
    number = forms.CharField(
        label='Número',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Número',
        }),
    )
    neighborhood = forms.CharField(
        label='Bairro',
        max_length=100,
        required=False,
    )
    city = forms.CharField(
        label='Cidade',
        max_length=100,
        required=False,
    )
    state = forms.ChoiceField(
        label='UF',
        choices=[("", "---")] + BRAZILIAN_STATES_BY_NAME,   # placeholder + lista
        required=False,
    )

    def get_user_data(self) -> dict:
        return {
            "email": self.cleaned_data["user_email"],
            "fullname": self.cleaned_data.get("user_fullname"),
        }


    def get_organization_data(self) -> dict:
        return {
            "company_name": self.cleaned_data["company_name"],
            "document": self.cleaned_data.get("document"),
            "phone": self.cleaned_data.get("phone", ""),
            "email": self.cleaned_data.get("company_email", ""),
            "zip_code": self.cleaned_data.get("zip_code", ""),
            "address": self.cleaned_data.get("address", ""),
            "neighborhood": self.cleaned_data.get("neighborhood", ""),
            "city": self.cleaned_data.get("city", ""),
            "state": self.cleaned_data.get("state", ""),
        }

    def clean_user_email(self):
        email = self.cleaned_data.get("user_email")
        if email:
            return email.strip().lower()
        return email
