# core/menu/registry_menu.py
from django.db.models import Prefetch, Q

from .base_menu import MenuGroup, MenuItem


class MenuRegistry:
    def __init__(self):
        self._groups = []

    def register(self, group):
        """Legacy. Menu agora vem do catálogo via DB."""
        self._groups.append(group)

    def clear(self):
        self._groups = []

    def get_menu(self, request):
        if not request.user.is_authenticated:
            return []

        from core.models import Module, ModuleItem

        ctx = getattr(request, "context", None)
        organization = getattr(ctx, "organization", None) if ctx else None
        system_roles = getattr(ctx, "system_roles", set()) if ctx else set()

        active_items_prefetch = Prefetch(
            "items",
            queryset=ModuleItem.objects.filter(is_active=True, show_in_menu=True),
        )

        base_qs = Module.objects.filter(
            is_active=True, show_in_menu=True
        ).prefetch_related(active_items_prefetch)

        # ── Filtros de scope ──
        scope_filter = Q(scope="global")  # global é sempre visível p/ autenticados

        if request.user.is_superuser:
            # Superuser vê tudo
            scope_filter |= Q(scope="superuser") | Q(scope="tenant")
        else:
            if "platform_admin" in system_roles:
                scope_filter |= Q(scope="superuser")

            if organization:
                scope_filter |= Q(
                    scope="tenant",
                    organization_modules__organization=organization,
                    organization_modules__is_active=True,
                )

        modules = base_qs.filter(scope_filter).distinct()

        # ── Monta grupos dinâmicos ──
        groups_to_check = list(self._groups)

        for module in modules:
            menu_items = [
                MenuItem(
                    label=item.name,
                    url_name=item.menu_url_name,
                    icon=item.icon or "circle",
                    permission=item.permission_codename(),
                    module=module.slug,
                    is_core=module.is_core,
                    is_universal=module.is_universal,
                    scope=module.scope,
                )
                for item in module.items.all()
            ]
            if not menu_items:
                continue

            groups_to_check.append(
                MenuGroup(
                    label=module.name,
                    icon=module.icon or "folder",
                    order=module.order,
                    scope=module.scope,
                    is_core=module.is_core,
                    is_universal=module.is_universal,
                    module=module.slug,
                    items=menu_items,
                )
            )

        # ── Render + dedupe por label ──
        seen = set()
        visible = []
        for group in groups_to_check:
            if group.label in seen:
                continue
            if not group.is_visible(request):
                continue
            items = group.get_visible_items(request)
            if not items:
                continue
            seen.add(group.label)
            visible.append({
                "label": group.label,
                "icon": group.icon,
                "order": group.order,
                "items": [
                    {
                        "label": it.label,
                        "url": it.get_url(request),
                        "icon": it.icon,
                        "permission": it.permission,
                    }
                    for it in items
                ],
            })

        return sorted(visible, key=lambda g: g.get("order", 0))


menu_registry = MenuRegistry()
