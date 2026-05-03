from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.enums.account import Gender
from core.forms import BaseForm

User = get_user_model()


class ClientCreateForm(BaseForm):
    fullname = forms.CharField(label=_('Nome Completo'), max_length=255, )
    email = forms.EmailField(label=_('E-mail'), )
    phone = forms.CharField(
        label=_('Telefone'),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'data-mask': 'phone'}),
    )
    gender = forms.ChoiceField(label=_('Gênero'), choices=Gender.choices, required=False, )
    cpf = forms.CharField(label=_('CPF'), max_length=14, required=False,
                          widget=forms.TextInput(attrs={'data-mask': 'cpf'}), )
    birth_date = forms.DateField(label=_('Data de Nascimento'), required=False,
                                 widget=forms.DateInput(
                                     attrs={'type': 'date', 'data-datepicker': 'data-datepicker', }), )

    # --- Atendimento (OrganizationClient) ---
    objective = forms.CharField(
        label=_('Objetivo'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('O que o cliente busca alcançar?'),
        }),
    )
    notes = forms.CharField(
        label=_('Observações internas'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Anotações privadas (não exibidas ao cliente)'),
        }),
    )

    confirm_link_user = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput,
    )

    FIELDSETS = (
        (_('Dados Pessoais'), ('fullname', 'email', 'cpf', 'phone', 'birth_date', 'gender')),
        (_('Atendimento'), ('objective', 'notes')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email_conflict = False

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_fullname(self):
        return self.cleaned_data['fullname'].strip()

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        if not cpf:
            return ''
        return cpf.strip()

    def clean(self):
        cleaned = super().clean()
        self._validate_email_conflict(cleaned)
        return cleaned

    def _validate_email_conflict(self, cleaned: dict) -> None:
        email = cleaned.get('email')
        if not email:
            return

        if not User.objects.filter(email__iexact=email).exists():
            return

        if cleaned.get('confirm_link_user'):
            return  # usuário já confirmou — segue o jogo

        self._email_conflict = True
        raise ValidationError(
            _('Já existe um usuário com este e-mail. '
              'Confirme abaixo para vinculá-lo à sua organização.')
        )

    def get_user_data(self) -> dict:
        keys = ('fullname', 'email', 'phone', 'gender', 'cpf', 'birth_date')
        return {k: self.cleaned_data.get(k) for k in keys}

    def get_organization_client_data(self) -> dict:
        keys = ('objective', 'notes')
        return {k: self.cleaned_data.get(k) for k in keys}

    @property
    def has_email_conflict(self) -> bool:
        return self._email_conflict


class ClientUpdateForm(ClientCreateForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['email'].help_text = _('Para alterar o e-mail, use o fluxo dedicado.')
