# core/menu/registry.py
from django.db.models import Prefetch
from .base import MenuGroup, MenuItem


class MenuRegistry:
    def __init__(self):
        self._groups = []

    def register(self, group):
        self._groups.append(group)

    def get_menu(self, request):
        visible = []

        # 1. Copia os menus estáticos (Global e Superuser registrados no menus.py)
        groups_to_check = list(self._groups)

        # 2. Carrega os Menus Dinâmicos da Clínica (Tenant)
        ctx = getattr(request, 'context', None)
        has_organization = bool(ctx and getattr(ctx, 'organization', None))

        if request.user.is_superuser or has_organization:

            from core.models import Module, ModuleItem

            # Otimização extrema: Prefetch apenas nos itens ativos
            # Se der erro aqui, mude 'items' para 'moduleitem_set'
            active_items_prefetch = Prefetch(
                'items',
                queryset=ModuleItem.objects.filter(is_active=True, show_in_menu=True)
            )

            # CORREÇÃO: Superuser carrega tudo. Usuário comum carrega só o da Clínica.
            if request.user.is_superuser:
                dynamic_modules = Module.objects.filter(
                    is_active=True,
                    show_in_menu=True
                ).prefetch_related(active_items_prefetch).distinct()
            else:
                dynamic_modules = Module.objects.filter(
                    is_active=True,
                    show_in_menu=True,
                    # Se der erro aqui, mude 'organization_modules' para 'organizationmodule'
                    organization_modules__organization=ctx.organization,
                    organization_modules__is_active=True
                ).prefetch_related(active_items_prefetch).distinct()

            # Transforma os Módulos do Banco em MenuGroup dinâmicos
            for module in dynamic_modules:
                menu_items = []

                # Se der erro aqui, mude 'items' para 'moduleitem_set'
                for item in module.items.all():
                    view_permission = f"view_{item.codename_prefix}"

                    menu_items.append(
                        MenuItem(
                            label=item.name,
                            url_name=getattr(item, 'url_name', '#'),
                            icon=getattr(item, 'icon', ''),
                            permission=view_permission
                        )
                    )

                if menu_items:
                    dynamic_group = MenuGroup(
                        label=module.name,
                        icon=getattr(module, 'icon', ''),
                        order=getattr(module, 'order', 0),
                        scope="tenant",
                        items=menu_items
                    )
                    groups_to_check.append(dynamic_group)

        # 3. Processa todos os grupos validados
        for group in groups_to_check:
            if group.is_visible(request):

                visible_items = group.get_visible_items(request)

                if visible_items:
                    visible.append({
                        "label": group.label,
                        "icon": group.icon,
                        "order": group.order,
                        "items": [
                            {
                                "label": item.label,
                                "url": item.get_url(request),
                                "icon": item.icon,
                                "permission": item.permission,
                            }
                            for item in visible_items
                        ],
                    })

        # Retorna o menu final ordenado pelo peso (order) de cada grupo
        return sorted(visible, key=lambda g: g.get("order", 0))

    def clear(self):
        self._groups = []


menu_registry = MenuRegistry()
