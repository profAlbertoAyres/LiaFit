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

        groups_to_check = list(self._groups)

        ctx = getattr(request, 'context', None)
        organization = getattr(ctx, 'organization', None) if ctx else None


        if request.user.is_superuser or organization:
            from core.models import Module, ModuleItem
            from django.db.models import Prefetch

            active_items_prefetch = Prefetch(
                'items',
                queryset=ModuleItem.objects.filter(is_active=True, show_in_menu=True)
            )

            if request.user.is_superuser:
                dynamic_modules = Module.objects.filter(
                    is_active=True,
                    show_in_menu=True
                ).prefetch_related(active_items_prefetch).distinct()
            else:
                dynamic_modules = Module.objects.filter(
                    is_active=True,
                    show_in_menu=True,
                    organization_modules__organization=organization,
                    organization_modules__is_active=True
                ).prefetch_related(active_items_prefetch).distinct()

            for module in dynamic_modules:
                menu_items = []

                for item in module.items.all():
                    menu_items.append(
                        MenuItem(
                            label=item.name,
                            url_name=item.menu_url_name,
                            icon=getattr(item, 'icon', ''),
                            permission=item.permission_codename()
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

        return sorted(visible, key=lambda g: g.get("order", 0))

    def clear(self):
        self._groups = []


menu_registry = MenuRegistry()
