# account/forms/member_form.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from account.models.member import RemunerationType
from account.models.profiles import RegistrationType
from core.enums.account import Gender
from core.forms import BaseForm
from account.models.specialty import Specialty

User = get_user_model()


class MemberCreateForm(BaseForm):
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

    remuneration_type = forms.ChoiceField(label=_('Tipo de Remuneração'), choices=RemunerationType.choices,
                                          initial=RemunerationType.FIXED, )
    joined_at = forms.DateField(label=_('Data de Admissão'), initial=timezone.localdate, widget=forms.DateInput(
        attrs={'type': 'text', 'data-datepicker': '', 'class': 'lia-form-control', 'placeholder': 'DD/MM/AAAA'}, ),
                                input_formats=['%d/%m/%Y', '%Y-%m-%d'], )

    is_professional = forms.BooleanField(
        label=_('Este membro é um profissional'),
        required=False,
    )
    registration_type = forms.ChoiceField(
        label=_('Tipo de Registro'),
        choices=RegistrationType.choices,
        required=False,
    )
    registration_number = forms.CharField(
        label=_('Nº Registro'),
        max_length=50,
        required=False,
    )
    specialties = forms.ModelMultipleChoiceField(
        label=_('Especialidades'),
        queryset=Specialty.objects.none(),
        required=False,
    )

    confirm_link_user = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput,
    )

    FIELDSETS = (
        (_('Dados Pessoais'), ('fullname', 'email', 'cpf', 'phone', 'birth_date', 'gender')),
        (_('Vínculo'), ('remuneration_type', 'joined_at')),
        (_('Profissional'), ('is_professional', 'registration_type',
                             'registration_number', 'specialties')),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._email_conflict = False
        self.fields['specialties'].queryset = Specialty.objects.filter(is_active=True)

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_fullname(self):
        return self.cleaned_data['fullname'].strip()

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        if not cpf:
            return ''

    def clean(self):
        cleaned = super().clean()
        self._validate_professional_fields(cleaned)
        self._validate_email_conflict(cleaned)
        return cleaned

    def _validate_professional_fields(self, cleaned: dict) -> None:
        if not cleaned.get('is_professional'):
            return

        if not cleaned.get('registration_type'):
            self.add_error('registration_type', _('Obrigatório para profissionais.'))

        if not cleaned.get('registration_number'):
            self.add_error('registration_number', _('Obrigatório para profissionais.'))

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

    def get_membership_data(self) -> dict:
        keys = ('remuneration_type', 'joined_at')
        return {k: self.cleaned_data.get(k) for k in keys}

    def get_professional_data(self) -> dict | None:
        if not self.cleaned_data.get('is_professional'):
            return None
        return {
            'registration_type': self.cleaned_data.get('registration_type'),
            'registration_number': self.cleaned_data.get('registration_number'),
            'specialties': self.cleaned_data.get('specialties'),
        }

    @property
    def has_email_conflict(self) -> bool:
        return self._email_conflict
