from django import forms

from account.models.user import User
from core.forms.base_form import BaseModelForm


class ProfileForm(BaseModelForm):
    """Form de edição do perfil pessoal do usuário autenticado."""

    class Meta:
        model = User
        fields = [
            'fullname',
            'phone',
            'birth_date',
            'gender',
            'photo',
        ]
        widgets = {
            'fullname': forms.TextInput(attrs={
                'autocomplete': 'name',
                'maxlength': 150,
            }),
            'phone': forms.TextInput(attrs={
                'autocomplete': 'tel',
                'inputmode': 'tel',
                'placeholder': '(11) 99999-9999',
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
            }),
            'gender': forms.Select(),
            'photo': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
            }),
        }

    def clean_photo(self):
        """Valida tipo e tamanho da foto (máx 5MB)."""
        photo = self.cleaned_data.get('photo')

        if photo and hasattr(photo, 'size'):
            max_size = 5 * 1024 * 1024  # 5MB
            if photo.size > max_size:
                raise forms.ValidationError(
                    'A foto deve ter no máximo 5MB.'
                )

            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            content_type = getattr(photo, 'content_type', '')
            if content_type and content_type not in allowed_types:
                raise forms.ValidationError(
                    'Formato inválido. Use JPG, PNG ou WEBP.'
                )

        return photo

    def clean_fullname(self):
        """Garante que o nome não fique vazio ou só com espaços."""
        fullname = self.cleaned_data.get('fullname', '').strip()
        if not fullname:
            raise forms.ValidationError('O nome é obrigatório.')
        return fullname
