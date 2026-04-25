from collections import defaultdict
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from core.models.permission import Permission
from core.models.role_permission import RolePermission


class RoleService:
    LEVEL_PROPRIETARIO = 100

    @staticmethod
    def update_role_permissions(role, user, user_level, selected_permission_ids, user_permissions_codenames):
        if not user.is_superuser and role.level >= user_level:
            raise PermissionDenied("Você não tem hierarquia para alterar as permissões deste papel.")

        is_tenant_owner = (user_level == 100)

        if not user.is_superuser and not is_tenant_owner:
            valid_permission_ids = list(Permission.objects.filter(
                id__in=selected_permission_ids,
                codename__in=user_permissions_codenames
            ).values_list('id', flat=True))

            selected_permission_ids = [str(pid) for pid in valid_permission_ids]

        role.role_permissions.all().delete()

        new_permissions = [
            RolePermission(
                role=role,
                permission_id=perm_id,
                organization=role.organization
            )
            for perm_id in selected_permission_ids
        ]

        RolePermission.objects.bulk_create(new_permissions)
        return True

    @staticmethod
    def get_role_context_flags(request, role):
        user = request.user
        active_modules = getattr(request.context, 'modules', [])

        is_superuser = user.is_superuser

        permissoes_qs = Permission.objects.select_related('item').all()

        if not is_superuser:
            module_names = []
            for m in active_modules:
                if hasattr(m, 'name'):
                    module_names.append(m.name)
                elif isinstance(m, str):
                    module_names.append(m)

            if module_names:
                permissoes_qs = permissoes_qs.filter(
                    Q(item__module__name__in=module_names) | Q(item__isnull=True)
                )

        permissoes_banco = list(permissoes_qs)

        permissoes_atuais = list(role.role_permissions.values_list('permission_id', flat=True))

        # 3. AGRUPANDO
        modulos_dict = defaultdict(lambda: defaultdict(list))

        for perm in permissoes_banco:
            # Pega o nome do Módulo Pai (Ex: Cadastros) para o Accordion
            if getattr(perm, 'item', None) and getattr(perm.item, 'module', None):
                nome_modulo = perm.item.module.name.title()
            else:
                nome_modulo = 'Sistema / Geral'

            # Pega o nome da Tela/Item (Ex: Clientes) para o Card
            if getattr(perm, 'item', None):
                nome_tela = perm.item.name.title()
            else:
                nome_tela = 'Geral'

            if not hasattr(perm, 'display_name') and hasattr(perm, 'name'):
                perm.display_name = perm.name

            modulos_dict[nome_modulo][nome_tela].append(perm)

        # Converte para lista para enviar ao Template HTML
        modules_with_permissions = []
        for nome_modulo, telas_dict in modulos_dict.items():
            lista_telas = []
            for nome_tela, perms in telas_dict.items():
                lista_telas.append({
                    'name': nome_tela,
                    'permissions': perms
                })
            # Ordena as telas (Cards) em ordem alfabética
            lista_telas.sort(key=lambda x: x['name'])

            modules_with_permissions.append({
                'name': nome_modulo,
                'items': lista_telas
            })

        # Ordena os módulos pais (Accordions) em ordem alfabética
        modules_with_permissions.sort(key=lambda x: x['name'])

        return {
            'permissoes_atuais_ids': permissoes_atuais,
            'modules_with_permissions': modules_with_permissions,
        }

    @staticmethod
    def process_role_permissions_update(request, role, membership, selected_permission_ids):
        # 1. EXTRAÇÃO DOS DADOS DO REQUEST
        user = request.user
        user_permissions = getattr(request.context, 'permissions', [])
        user_level = membership.highest_role_level if membership else 0

        if user.is_superuser or 'change_configuracoes_role_permission' in user_permissions:
            RoleService.update_role_permissions(
                role=role,
                user=user,
                user_level=user_level,
                selected_permission_ids=selected_permission_ids,
                user_permissions_codenames=user_permissions
            )
            return True

        return False

    @staticmethod
    def filter_visible_roles(request, queryset, membership):
        user = request.user
        organization = request.context.organization

        qs = queryset.exclude(level=RoleService.LEVEL_PROPRIETARIO)

        if user.is_superuser or organization.owner_id == user.id:
            return qs

        if membership:
            user_level = membership.highest_role_level
            return queryset.filter(level__lt=user_level)

        return qs.none()

    @staticmethod
    def check_hierarchy_permission(request, role, membership):
        user = request.user
        organization = request.context.organization

        if user.is_superuser or organization.owner_id == user.id:
            return True

        user_level = membership.highest_role_level if membership else 0

        if role.level >= user_level:
            raise PermissionDenied(
                f"Você não tem hierarquia para interagir com este cargo. "
                f"Seu nível máximo é {user_level} e o cargo exige nível {role.level} ou inferior."
            )
        return True
