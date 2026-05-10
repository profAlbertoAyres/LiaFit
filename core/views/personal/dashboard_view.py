from django.views.generic import TemplateView

from core.services.personal_dashboard_service import PersonalDashboardService
from core.views.base_view import BaseAuthMixin


class PersonalDashboardView(BaseAuthMixin, TemplateView):
    """
    Dashboard pessoal do usuário autenticado.

    Renderizada em `/personal/dashboard/`, é a tela inicial após login
    quando o usuário NÃO está em contexto de organização (tenant).

    Mostra:
        - Saudação personalizada
        - Lista de organizações que o usuário participa
        - Atalhos rápidos (criar org, aceitar convites, etc.)
        - Atividades recentes do próprio usuário
    """

    template_name = 'core/personal/dashboard.html'
    permission_required = None
    require_tenant = False  # 🔑 espaço pessoal NÃO exige tenant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        dashboard_data = PersonalDashboardService.get_dashboard_data(user=user)

        context.update({
            'user': user,
            'organizations': dashboard_data.get('organizations', []),
            'pending_invites': dashboard_data.get('pending_invites', []),
            'recent_activities': dashboard_data.get('recent_activities', []),
            'quick_stats': dashboard_data.get('quick_stats', {}),
        })
        return context
