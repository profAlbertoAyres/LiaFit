from collections import defaultdict
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from core.models import Module
from core.models.permission import Permission
from core.models.role_permission import RolePermission
from core.services.permission_service import is_saas_staff  # 🆕


class RoleService:
    LEVEL_PROPRIETARIO = 100

    # ============================================================
    # 🔐 HELPERS DE PRIVILÉGIO
    # ============================================================

    @staticmethod
    def _is_full_editor(user, organization, user_level: int) -> bool:
        """
        Quem pode editar TODAS as permissões (mesmo as que não possui)?
          • Superuser (Django)
          • SaaS staff (equipe interna)
          • Owner do tenant
        """
        if user.is_superuser or is_saas_staff(user):
            return True
        if organization.owner_id == user.id:
            return True
        if user_level >= RoleService.LEVEL_PROPRIETARIO:
            return True
        return False

    @staticmethod
    def _get_universal_permission_ids() -> set:
        """
        IDs de permissões INALIENÁVEIS (módulos universais).
        Essas NUNCA podem ser removidas de um role.
        """
        return set(
            Permission.objects.filter(
                item__module__is_universal=True,
                is_active=True,
            ).values_list('id', flat=True)
        )

    # ============================================================
    # ✏️ ATUALIZAÇÃO DE PERMISSÕES (Filosofia C + universais)
    # ============================================================

    @staticmethod
    def update_role_permissions(
        role,
        user,
        user_level,
        selected_permission_ids,
        user_permissions_codenames,
    ):
        """
        Atualiza permissões do Role respeitando:
          1. Hierarquia (não mexer em role >= seu nível)
          2. Filosofia C (só edita permissões que VOCÊ possui)
          3. Universais (sempre presentes, jamais removíveis)
        """
        organization = role.organization

        if role.level >= RoleService.LEVEL_PROPRIETARIO:
            raise PermissionDenied(
                "O papel de Proprietário é imutável e não pode ter suas permissões alteradas."
            )

        # 1) Hierarquia
        if not user.is_superuser and not is_saas_staff(user):
            if role.level >= user_level and organization.owner_id != user.id:
                raise PermissionDenied(
                    "Você não tem hierarquia para alterar as permissões deste papel."
                )

        # 2) Conjunto de IDs vindos do POST (normalizado p/ string)
        selected_ids = {str(pid) for pid in selected_permission_ids}

        # 3) Universais: SEMPRE concedidas (mesmo se o user esquecer de marcar)
        universal_ids = {str(pid) for pid in RoleService._get_universal_permission_ids()}

        # 4) Quem é "editor pleno" (substitui tudo)?
        full_editor = RoleService._is_full_editor(user, organization, user_level)

        if full_editor:
            # Owner/superuser/saas_staff: substitui tudo + força universais
            new_permissions_ids = selected_ids | universal_ids
        else:
            # 🛡️ Filosofia C: só mexe no que o user PODE editar
            codenames_set = set(user_permissions_codenames)

            editable_perms_ids = {
                str(pid) for pid in Permission.objects.filter(
                    codename__in=codenames_set
                ).values_list('id', flat=True)
            }

            # Universais NÃO entram no editável (são intocáveis)
            editable_perms_ids -= universal_ids

            # Do POST, mantém só o que é editável
            selected_editable = selected_ids & editable_perms_ids

            # IDs intocáveis = (todas que role tem, exceto editáveis) + universais
            existing_ids = {
                str(pid) for pid in role.role_permissions.values_list(
                    'permission_id', flat=True
                )
            }
            untouchable_ids = (existing_ids - editable_perms_ids) | universal_ids

            # Final = intocáveis (preservadas) + editáveis selecionadas
            new_permissions_ids = untouchable_ids | selected_editable

        # 5) Sincronização: deleta tudo, recria
        role.role_permissions.all().delete()

        new_permissions = [
            RolePermission(
                role=role,
                permission_id=int(perm_id),
                organization=organization,
            )
            for perm_id in new_permissions_ids
        ]
        RolePermission.objects.bulk_create(new_permissions)
        return True

    # ============================================================
    # 🎨 CONTEXTO PRA TEMPLATE
    # ============================================================

    @staticmethod
    def get_role_context_flags(request, role):
        """
        Monta o contexto da tela de detalhe do Role (Filosofia C).

        Retorna:
          • permissoes_atuais_ids: ids já vinculadas (marcam o checkbox)
          • modules_with_permissions: agrupado Módulo → Tela → Permissions
              cada perm tem flags:
                - perm.is_editable    (Filosofia C)
                - perm.is_universal   (módulo universal — INALIENÁVEL)
          • can_edit_all_permissions: user pode editar tudo? (owner/superuser/saas)
          • can_change_permissions:   user pode salvar o form? (RBAC)
        """
        from core.models import OrganizationModule

        user = request.user
        organization = request.context.organization
        membership = getattr(request.context, 'membership', None)
        user_permissions_codenames = set(getattr(request.context, 'permissions', []))

        user_level = membership.highest_role_level if membership else 0

        # 🔐 Pode editar TUDO?
        can_edit_all = RoleService._is_full_editor(user, organization, user_level)

        # 🔐 Pode salvar o form? (precisa da permissão settings.change_role)
        can_change_permissions = (
            user.is_superuser
            or is_saas_staff(user)
            or organization.owner_id == user.id
            or 'settings.change_role' in user_permissions_codenames
        )

        # 🌐 IDs de permissões universais (intocáveis)
        universal_ids = RoleService._get_universal_permission_ids()

        # 1) Permissões dos módulos ATIVOS na organização
        active_module_ids = OrganizationModule.objects.filter(
            organization=organization,
            is_active=True,
        ).values_list('module_id', flat=True)

        permissoes_qs = (
            Permission.objects
            .select_related('item__module')
            .filter(is_active=True)
            .filter(
                Q(item__module_id__in=active_module_ids) | Q(item__isnull=True)
            ).exclude(item__module__scope=Module.Scope.SUPERUSER)

        )
        permissoes_banco = list(permissoes_qs)

        # 2) IDs já vinculadas ao role
        permissoes_atuais = list(
            role.role_permissions.values_list('permission_id', flat=True)
        )

        # 3) Agrupamento Módulo → Tela → [Permissions]
        modulos_dict = defaultdict(lambda: defaultdict(list))

        for perm in permissoes_banco:
            # 🌐 É universal? (intocável por todos, exceto sync_system_catalog)
            perm.is_universal = perm.id in universal_ids

            # 🛡️ Filosofia C: editor pleno OU usuário possui essa perm?
            user_owns = perm.codename in user_permissions_codenames
            perm.is_editable = (can_edit_all or user_owns) and not perm.is_universal

            # Nome do Módulo Pai (Accordion)
            if getattr(perm, 'item', None) and getattr(perm.item, 'module', None):
                nome_modulo = perm.item.module.name.title()
            else:
                nome_modulo = 'Sistema / Geral'

            # Nome da Tela/Item (Card)
            if getattr(perm, 'item', None):
                nome_tela = perm.item.name.title()
            else:
                nome_tela = 'Geral'

            # display_name (fallback)
            if not getattr(perm, 'display_name', None):
                perm.display_name = (
                    perm.get_action_display()
                    if hasattr(perm, 'get_action_display')
                    else perm.action.title()
                )

            modulos_dict[nome_modulo][nome_tela].append(perm)

        # 4) Converte e ordena alfabeticamente
        modules_with_permissions = []
        for nome_modulo, telas_dict in modulos_dict.items():
            lista_telas = [
                {'name': nome_tela, 'permissions': perms}
                for nome_tela, perms in telas_dict.items()
            ]
            lista_telas.sort(key=lambda x: x['name'])

            modules_with_permissions.append({
                'name': nome_modulo,
                'items': lista_telas,
            })

        modules_with_permissions.sort(key=lambda x: x['name'])

        return {
            'permissoes_atuais_ids': permissoes_atuais,
            'modules_with_permissions': modules_with_permissions,
            'can_edit_all_permissions': can_edit_all,
            'can_change_permissions': can_change_permissions,  # 🆕
        }

    # ============================================================
    # 🧭 ROTEAMENTO DO POST
    # ============================================================

    @staticmethod
    def process_role_permissions_update(request, role, membership, selected_permission_ids):
        """
        Decide se o user pode atualizar permissões do role e delega pro update.
        """
        user = request.user
        user_permissions = getattr(request.context, 'permissions', [])
        user_level = membership.highest_role_level if membership else 0

        can_change = (
            user.is_superuser
            or is_saas_staff(user)
            or request.context.organization.owner_id == user.id
            or 'settings.change_role' in user_permissions  # 🆕 padronizado
        )

        if can_change:
            RoleService.update_role_permissions(
                role=role,
                user=user,
                user_level=user_level,
                selected_permission_ids=selected_permission_ids,
                user_permissions_codenames=user_permissions,
            )
            return True

        return False

    # ============================================================
    # 🔍 VISIBILIDADE / HIERARQUIA
    # ============================================================


    @staticmethod
    def filter_visible_roles(request, queryset, membership):
        user = request.user
        organization = request.context.organization

        # 🔒 Role 'owner' nunca é listado (nem pro próprio owner) — é imutável
        qs = queryset.exclude(level=RoleService.LEVEL_PROPRIETARIO)

        if user.is_superuser or is_saas_staff(user) or organization.owner_id == user.id:
            return qs

        if membership:
            user_level = membership.highest_role_level
            return qs.filter(level__lt=user_level)

        return qs.none()

    @staticmethod
    def check_hierarchy_permission(request, role, membership):
        user = request.user
        organization = request.context.organization

        if user.is_superuser or is_saas_staff(user) or organization.owner_id == user.id:
            return True

        user_level = membership.highest_role_level if membership else 0

        if role.level >= user_level:
            raise PermissionDenied(
                f"Você não tem hierarquia para interagir com este cargo. "
                f"Seu nível máximo é {user_level} e o cargo exige nível {role.level} ou inferior."
            )
        return True
