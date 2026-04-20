# core/filters/tenant.py
import django_filters
from core.filters.base import BaseFilter
from core.models import RolePermission, UserPermission, Role, Permission
from django.contrib.auth import get_user_model

User = get_user_model()


class RolePermissionFilter(BaseFilter):
    # O cliente pode querer filtrar as permissões por "Cargo" (Role)
    role = django_filters.ModelChoiceFilter(
        queryset=Role.objects.none(),  # Iniciamos vazio por segurança
        label="Cargo",
        empty_label="Todos os Cargos"
    )

    class Meta:
        model = RolePermission
        fields = ['role']
        # Busca pelo nome do cargo ou pelo nome da permissão
        search_fields = ['role__name', 'permission__name']

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, request=request, **kwargs)
        # 💥 FILTRO SEGURO NO DROPDOWN DE BUSCA:
        # Garante que no filtro de "Cargos", o Dr. João só veja os cargos da clínica dele
        if self.organization:
            self.form.fields['role'].queryset = Role.objects.filter(
                organization=self.organization
            )


class UserPermissionFilter(BaseFilter):
    # O cliente pode querer filtrar as permissões por "Usuário/Funcionário"
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.none(),
        label="Usuário",
        empty_label="Todos os Usuários"
    )

    class Meta:
        model = UserPermission
        fields = ['user']
        # Busca pelo nome/email do usuário ou pelo nome da permissão
        search_fields = ['user__first_name', 'user__email', 'permission__name']

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, request=request, **kwargs)
        # 💥 FILTRO SEGURO:
        # O Dr. João só pode filtrar pelos usuários que pertencem à clínica dele
        if self.organization:
            # Assumindo que você tem uma relação do usuário com a clínica
            # Ajuste o 'user__professional_assignments__organization' conforme seu model real
            self.form.fields['user'].queryset = User.objects.filter(
                professional_assignments__organization=self.organization
            ).distinct()
