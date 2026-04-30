# core/services/dashboard_service.py
from django.urls import reverse

from account.models import OrganizationClient, OrganizationMember


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

    @staticmethod
    def get_redirect_url(request) -> str | None:
        """
        Retorna:
          - URL (str) → a view deve redirecionar
          - None      → a view segue o fluxo normal
        """
        # Se a URL já tem slug, não precisa redirecionar
        if 'org_slug' in request.resolver_match.kwargs:
            return None

        # Usuário não autenticado → não é nossa responsabilidade
        if not request.user.is_authenticated:
            return None

        # Busca organização ativa
        slug = DashboardService._get_user_org_slug(request.user)

        # Tem org → manda pra rota com slug
        if slug:
            return reverse('tenant:dashboard', kwargs={'org_slug': slug})

        # Não tem org → segue o fluxo (renderiza sem slug)
        return None

    @staticmethod
    def _get_user_org_slug(user) -> str | None:
        membership = (
            OrganizationMember.objects
            .filter(user=user, is_active=True, organization__is_active=True)
            .select_related('organization')
            .first()
        )
        return membership.organization.slug if membership else None
