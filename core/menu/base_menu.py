# core/menu/base_menu.py
from django.urls import reverse, NoReverseMatch


class MenuNode:
    def _check_scope(self, request):
        if request.user.is_superuser:
            return True

        ctx = getattr(request, "context", None)
        system_roles = getattr(ctx, "system_roles", set()) if ctx else set()

        if self.scope == "superuser":
            return "saas-admin" in system_roles or "superadmin" in system_roles

        if self.scope == "tenant":
            return bool(ctx and getattr(ctx, "organization", None))

        if self.scope == "global":
            return request.user.is_authenticated

        return True

    def _check_module(self, request):
        if getattr(self, "is_universal", False):
            return True
        if self.is_core or not self.module:
            return True
        ctx = getattr(request, "context", None)
        return bool(ctx and self.module in ctx.modules)

    def _check_permission(self, request):
        if not self.permission:
            return True
        if getattr(self, "is_universal", False):
            return True
        ctx = getattr(request, "context", None)
        if ctx and self.permission in ctx.permissions:
            return True
        return request.user.has_perm(self.permission)


class MenuItem(MenuNode):
    def __init__(
        self,
        label,
        url_name,
        icon="circle",
        permission=None,
        module=None,
        is_core=False,
        is_universal=False,
        scope="tenant",
    ):
        self.label = label
        self.url_name = url_name
        self.icon = icon
        self.permission = permission
        self.module = module
        self.is_core = is_core
        self.is_universal = is_universal
        self.scope = scope

    def get_url(self, request):
        try:
            ctx = getattr(request, "context", None)
            org = getattr(ctx, "organization", None) if ctx else None
            if org:
                try:
                    return reverse(self.url_name, kwargs={"org_slug": org.slug})
                except NoReverseMatch:
                    pass
            return reverse(self.url_name)
        except NoReverseMatch:
            return "#"

    def is_visible(self, request):
        return (
            self._check_scope(request)
            and self._check_module(request)
            and self._check_permission(request)
        )


class MenuGroup(MenuNode):
    def __init__(
        self,
        label,
        items,
        icon="folder",
        permission=None,
        module=None,
        is_core=False,
        is_universal=False,
        order=0,
        scope="tenant",
    ):
        self.label = label
        self.items = items
        self.icon = icon
        self.permission = permission
        self.module = module
        self.is_core = is_core
        self.is_universal = is_universal
        self.order = order
        self.scope = scope

    def get_visible_items(self, request):
        return [item for item in self.items if item.is_visible(request)]

    def is_visible(self, request):
        if not self._check_scope(request):
            return False
        if not self._check_module(request):
            return False
        if not self._check_permission(request):
            return False
        return bool(self.get_visible_items(request))
