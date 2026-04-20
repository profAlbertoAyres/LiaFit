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


class RolePermissionForm(BaseModelForm):

    class Meta:
        model = RolePermission
        fields = ['role', 'permission']

        labels = {
            'role': _('Papel / Cargo'),
            'permission': _('Permissão de Acesso'),
        }
