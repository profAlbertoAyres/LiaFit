from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms.base import BaseModelForm
from core.models import Role
from core.models.role_permission import RolePermission


class RoleForm(BaseModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'level', 'is_active']

        labels = {
            'name': _('Nome do Papel (Cargo)'),
            'description': _('Descrição'),
            'level': _('Nível de Acesso (Hierarquia)'),
            'is_active': _('Ativo'),
        }

        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_level(self):
        level = self.cleaned_data.get('level')

        # O membership já vem injetado pela sua classe BaseModelForm!
        if self.membership and not self.membership.user.is_superuser:
            user_level = self.membership.highest_role_level

            # Trava matemática: não pode criar papel com nível maior ou igual ao dele
            if level >= user_level:
                raise forms.ValidationError(
                    f"Você só pode criar ou editar papéis com nível menor que o seu (Seu nível máximo atual é {user_level})."
                )

        return level

class RolePermissionForm(BaseModelForm):

    class Meta:
        model = RolePermission
        fields = ['role', 'permission']

        labels = {
            'role': _('Papel / Cargo'),
            'permission': _('Permissão de Acesso'),
        }
