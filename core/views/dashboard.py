from django.views.generic import TemplateView

from core.views.base import BaseAuthMixin, ContextMixin


class DashboardView(ContextMixin, BaseAuthMixin, TemplateView):
    """Dashboard principal da organização."""

    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ctx = self.request.context

        context.update({
            'organization': ctx.organization,
            'membership': ctx.membership,
            'roles': ctx.roles,
            'modules': ctx.modules,
        })

        return context
