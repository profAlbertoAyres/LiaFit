# account/forms/profile_form.py
from django import forms
from django.utils.translation import gettext_lazy as _

from account.models.user import User
from core.forms.base_form import BaseModelForm


class ProfileForm(BaseModelForm):
    """Form de edição do perfil pessoal do usuário autenticado."""

    FIELDSETS = (
        (_('Dados Pessoais'), ('fullname', 'cpf', 'phone', 'birth_date', 'gender')),
        (_('Foto'), ('photo',)),
    )

    class Meta:
        model = User
        fields = ['fullname', 'cpf', 'phone', 'birth_date', 'gender', 'photo']
        widgets = {
            'fullname': forms.TextInput(attrs={
                'autocomplete': 'name',
                'maxlength': 150,
            }),
            'cpf': forms.TextInput(attrs={
                'data-mask': 'cpf',
                'maxlength': 14,
                'autocomplete': 'off',
                'inputmode': 'numeric',
            }),
            'phone': forms.TextInput(attrs={
                'data-mask': 'phone',
                'autocomplete': 'tel',
                'inputmode': 'tel',
                'placeholder': '(11) 99999-9999',
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'data-iu-input': '',
            }),
        }

    def clean_fullname(self):
        fullname = (self.cleaned_data.get('fullname') or '').strip()
        if not fullname:
            raise forms.ValidationError(_('O nome é obrigatório.'))
        return fullname

    def clean_cpf(self):
        cpf = (self.cleaned_data.get('cpf') or '').strip()
        if cpf:
            digits = ''.join(filter(str.isdigit, cpf))
            if len(digits) != 11:
                raise forms.ValidationError(_('CPF inválido.'))
        return cpf

    def clean_phone(self):
        return (self.cleaned_data.get('phone') or '').strip()

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size'):
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('A foto deve ter no máximo 5MB.'))

            allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
            content_type = getattr(photo, 'content_type', '') or ''
            if content_type and content_type not in allowed_types:
                raise forms.ValidationError(_('Formato inválido. Use JPG, PNG ou WEBP.'))
        return photo
