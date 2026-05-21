from django import forms
from django.utils.translation import gettext_lazy as _


from account.models import Organization
from core.forms.base_form import BaseModelForm


class OrganizationUpdateForm(BaseModelForm):

    FIELDSETS = (
        (_('Dados da Empresa'), (
            'company_name', 'document', 'email', 'phone', 'logo',
        )),
        (_('Endereço'), (
            'zip_code', 'address', 'number',
            'neighborhood', 'city', 'state',
        )),
    )

    class Meta:
        model = Organization
        fields = [
            'company_name', 'document', 'email', 'phone', 'logo',
            'zip_code', 'address', 'number',
            'neighborhood', 'city', 'state',
        ]
        widgets = {
            'document': forms.TextInput(attrs={'data-mask': 'cnpj_cpf'}),
            'phone':    forms.TextInput(attrs={'data-mask': 'phone', 'type': 'tel'}),
            'zip_code': forms.TextInput(attrs={'data-mask': 'cep'}),
            'logo': forms.ClearableFileInput(attrs={
                'accept': 'image/jpeg,image/png,image/webp,image/gif',
                'data-fu-input': '',
            }),
        }

    def clean_company_name(self):
        return self.cleaned_data['company_name'].strip()

    def clean_email(self):
        email = self.cleaned_data.get('email') or ''
        return email.strip().lower()