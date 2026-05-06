# core/services/dashboard_service.py
from account.models import OrganizationClient
from core.services.space_service import get_user_spaces


class DashboardService:
    """
    Serviço que consolida regras do Dashboard:
      - Decisão de redirect pós-login (baseada em espaços)
      - Métricas e dados de exibição (quando dentro de uma org)
    """

    # ------------------------------------------------------------------
    # Decisão de redirect (chamada pela DashboardView.dispatch)
    # ------------------------------------------------------------------

    @staticmethod
    def get_redirect_url(request) -> str | None:
        """
        Retorna:
          - URL (str) → a view deve redirecionar
          - None      → a view renderiza o template (cards ou vazio)

        Regras:
          1. Se já estamos dentro de um tenant (URL com org_slug) → não redireciona
          2. Se user não autenticado → não é nossa responsabilidade
          3. Se user tem exatamente 1 espaço → redireciona pra ele (auto-entra)
          4. Se user tem 0 ou 2+ espaços → renderiza template
        """
        # 1. Já está em rota de tenant → segue normal
        if 'org_slug' in request.resolver_match.kwargs:
            return None

        # 2. Não autenticado → deixa o auth tratar
        if not request.user.is_authenticated:
            return None

        # 3. Auto-entra se tiver só 1 espaço
        spaces = get_user_spaces(request.user)
        if len(spaces) == 1:
            return spaces[0]['url']

        # 4. 0 ou 2+ espaços → renderiza
        return None

    # ------------------------------------------------------------------
    # Dados de exibição (quando dentro de uma organização)
    # ------------------------------------------------------------------

    @staticmethod
    def get_dashboard_data(organization, membership=None) -> dict:
        """
        Retorna métricas e dados de exibição do dashboard de uma org.
        Quando não há organization, retorna estrutura vazia.
        """
        if not organization:
            return {
                'metrics': {},
                'recent_clients': [],
            }

        total_clients = OrganizationClient.objects.filter(
            organization=organization
        ).count()

        recent_clients = (
            OrganizationClient.objects
            .filter(organization=organization)
            .select_related('user')
            .order_by('-created_at')[:5]
        )

        return {
            'metrics': {
                'total_clients': total_clients,
                'total_team': 0,
                'today_appointments': 0,
                'monthly_revenue': 0.0,
            },
            'recent_clients': recent_clients,
        }
