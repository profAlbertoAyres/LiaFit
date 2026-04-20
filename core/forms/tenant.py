# core/forms/tenant.py
from core.forms.base import BaseModelForm
from core.models.role_permission import RolePermission
from core.models.user_permission import UserPermission


class RolePermissionForm(BaseModelForm):
    class Meta:
        model = RolePermission
        fields = ['role', 'permission']


class UserPermissionForm(BaseModelForm):
    class Meta:
        model = UserPermission
        fields = ['user', 'permission']