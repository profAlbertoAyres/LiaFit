from django.shortcuts import redirect
from django.views.generic import TemplateView

# Suas importações existentes
from core.services.post_login import resolve_post_login_redirect
from core.services.deshboard_service import DashboardService
from core.views.base import BaseAuthMixin, ContextMixin


class DashboardView(ContextMixin, BaseAuthMixin, TemplateView):
    template_name = 'core/dashboard/dashboard.html'
    permission_required = None

    def dispatch(self, request, *args, **kwargs):
        # Se NÃO tem org_slug na URL (ou seja, ele digitou lialinda.com.br/dashboard)
        if 'org_slug' not in kwargs:
            last_org_slug = request.session.get('last_org_slug')

            # Usamos o SEU service para descobrir para onde ele deveria ir
            redirect_url, _ = resolve_post_login_redirect(request.user, last_org_slug)

            # Evita loop infinito: só redireciona se a URL destino for diferente da atual
            if redirect_url != request.path:
                return redirect(redirect_url)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ctx = self.request.context  # Preenchido pelo seu ContextMixin

        # O ctx.organization virá preenchido pelo BaseAuthMixin/ContextMixin
        # se tiver na URL, ou None se for cliente global
        dashboard_data = DashboardService.get_dashboard_data(
            organization=ctx.organization,
            membership=ctx.membership
        )

        context.update({
            'organization': ctx.organization,
            'membership': ctx.membership,
            'roles': getattr(ctx, 'roles', []),
            'modules': getattr(ctx, 'modules', []),
            'metrics': dashboard_data.get('metrics'),
            'recent_clients': dashboard_data.get('recent_clients'),
        })

        return context
