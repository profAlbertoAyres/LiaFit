# core/services/dashboard_service.py
from account.models import OrganizationClient


class DashboardService:
    """
    Serviço de dados do Dashboard de uma organização.

    Responsabilidade única: agregar métricas e listagens
    para exibição no template do dashboard.

    Nota: A decisão de redirect pós-login (hub de espaços) é
    responsabilidade do SpaceHubService, na rota /dashboard/.
    """

    @staticmethod
    def get_dashboard_data(organization, membership=None) -> dict:
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
