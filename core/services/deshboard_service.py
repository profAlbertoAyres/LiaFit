# core/services/dashboard.py
from account.models import OrganizationClient

class DashboardService:
    """
    Serviço que consolida as regras de negócio e métricas do Dashboard.
    Isolado por tenant (organization).
    """

    @staticmethod
    def get_dashboard_data(organization, membership=None) -> dict:
        """
        Retorna os dados necessários para o dashboard da clínica.
        """
        if not organization:
            return {
                'metrics': {},
                'recent_clients': [],
            }

        # 1. Métrica: Total de Clientes Ativos
        # Usando o ActiveClientManager que você criou (arquivados não entram)
        total_clients = OrganizationClient.objects.filter(
            organization=organization
        ).count()

        # 2. Lista: Últimos 5 clientes cadastrados
        # select_related('user') evita N+1 queries ao exibir o nome/email na tabela
        recent_clients = OrganizationClient.objects.filter(
            organization=organization
        ).select_related('user').order_by('-created_at')[:5]

        # Retornamos placeholders zerados para os widgets futuros para não quebrar o HTML
        return {
            'metrics': {
                'total_clients': total_clients,
                'total_team': 0,          
                'today_appointments': 0,
                'monthly_revenue': 0.0,
            },
            'recent_clients': recent_clients
        }
