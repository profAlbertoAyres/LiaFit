# core/menu/base.py
from django.urls import reverse, NoReverseMatch


class MenuItem:
    def __init__(self, label, url_name, icon="circle", permission=None):
        self.label = label
        self.url_name = url_name
        self.icon = icon
        self.permission = permission

    def get_url(self, request):
        try:
            ctx = getattr(request, 'context', None)
            if ctx and ctx.organization:
                try:
                    return reverse(self.url_name, kwargs={'org_slug': ctx.organization.slug})
                except NoReverseMatch:
                    pass
            return reverse(self.url_name)
        except NoReverseMatch:
            return "#"

    def is_visible(self, request):
        # 🔥 MODO DESENVOLVIMENTO: Ignora permissões e mostra todos os itens!
        # Para ativar a segurança novamente no futuro, apague este "return True"
        # e descomente o bloco de código abaixo.
        return True

        """
        if not self.permission:
            return True

        if request.user.is_superuser:
            return True

        ctx = getattr(request, 'context', None)
        if ctx and hasattr(ctx, 'permissions'):
            perm_list = [p.codename if hasattr(p, 'codename') else p for p in ctx.permissions]
            permission_codename = self.permission.split('.')[-1] if '.' in self.permission else self.permission

            if self.permission in perm_list or permission_codename in perm_list:
                return True

        return request.user.has_perm(self.permission)
        """


class MenuGroup:
    def __init__(self, label, items, icon="folder", permission=None, order=0, scope="tenant"):
        self.label = label
        self.items = items
        self.icon = icon
        self.permission = permission
        self.order = order
        self.scope = scope

    def get_visible_items(self, request):
        return [item for item in self.items if item.is_visible(request)]

    def is_visible(self, request):
        if self.scope == 'superuser' and not request.user.is_superuser:
            return False

        if self.scope == 'tenant':
            if not request.user.is_superuser:
                ctx = getattr(request, 'context', None)
                if not ctx or not getattr(ctx, 'membership', None):
                    return False

        # 🔥 MODO DESENVOLVIMENTO: Ignora permissão de grupo
        # Descomente no futuro para reativar
        """
        if self.permission:
            if not request.user.is_superuser:
                ctx = getattr(request, 'context', None)
                has_tenant_perm = False
                if ctx and hasattr(ctx, 'permissions'):
                    perm_list = [p.codename if hasattr(p, 'codename') else p for p in ctx.permissions]
                    has_tenant_perm = self.permission in perm_list

                has_global_perm = request.user.has_perm(self.permission)

                if not (has_tenant_perm or has_global_perm):
                    return False
        """

        # Só mostra o grupo se tiver pelo menos 1 item visível dentro dele
        return len(self.get_visible_items(request)) > 0
