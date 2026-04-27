# core/forms/master_view.py
from core.forms.base_form import BaseModelForm
from core.models import Module, Permission, Role

class ModuleForm(BaseModelForm):
    class Meta:
        model = Module
        fields = ['name', 'slug','is_core']

class PermissionForm(BaseModelForm):
    class Meta:
        model = Permission
        fields = ['item', 'action', 'name', 'codename', 'description']

class RoleForm(BaseModelForm):
    class Meta:
        model = Role
        fields = ['name', 'level','description']
