from django.shortcuts import redirect
from django.views.generic import TemplateView

from core.services.dashboard_service import DashboardService
from core.views.base_view import BaseAuthMixin, TenantContextMixin


class DashboardView(TenantContextMixin, BaseAuthMixin, TemplateView):
    template_name = 'core/dashboard/dashboard.html'
    permission_required = None
    require_tenant = False

    def dispatch(self, request, *args, **kwargs):
        # Pergunta pro service: preciso redirecionar?
        redirect_url = DashboardService.get_redirect_url(request)
        if redirect_url:
            return redirect(redirect_url)

        # Service disse que não → segue o fluxo normal
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ctx = getattr(self.request, 'context', None)

        organization = getattr(ctx, 'organization', None) if ctx else None
        membership = getattr(ctx, 'membership', None) if ctx else None

        dashboard_data = DashboardService.get_dashboard_data(
            organization=organization,
            membership=membership,
        )

        context.update({
            'organization': organization,
            'membership': membership,
            'roles': getattr(ctx, 'roles', []) if ctx else [],
            'modules': getattr(ctx, 'modules', []) if ctx else [],
            'metrics': dashboard_data.get('metrics'),
            'recent_clients': dashboard_data.get('recent_clients'),
        })
        return context