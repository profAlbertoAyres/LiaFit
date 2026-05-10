"""
Serviço do dashboard pessoal do usuário.

Centraliza a montagem dos dados exibidos em `/personal/dashboard/`.
Independente de organização (tenant) — opera sobre o próprio usuário.
"""

from typing import Any


class PersonalDashboardService:
    """
    Service responsável por agregar dados do espaço pessoal.

    Padrão espelha o `DashboardService` do tenant, mas o sujeito
    central aqui é o `User`, não a `Organization`.
    """

    @staticmethod
    def get_dashboard_data(user) -> dict[str, Any]:
        """
        Retorna o pacote de dados do dashboard pessoal.

        Args:
            user: instância de `User` autenticado.

        Returns:
            dict com as chaves:
                - organizations:      list[Organization] do usuário
                - pending_invites:    list[Invite] pendentes
                - recent_activities:  list[Activity] recentes
                - quick_stats:        dict com contadores rápidos
        """
        return {
            'organizations': PersonalDashboardService._get_user_organizations(user),
            'pending_invites': PersonalDashboardService._get_pending_invites(user),
            'recent_activities': PersonalDashboardService._get_recent_activities(user),
            'quick_stats': PersonalDashboardService._get_quick_stats(user),
        }

    # ------------------------------------------------------------------
    # Métodos auxiliares — esqueletos a serem implementados depois
    # ------------------------------------------------------------------

    @staticmethod
    def _get_user_organizations(user) -> list:
        """Lista de organizações que o usuário participa.

        TODO: implementar com base no model de Membership.
        Ex.: Organization.objects.filter(memberships__user=user, memberships__is_active=True)
        """
        return []

    @staticmethod
    def _get_pending_invites(user) -> list:
        """Convites pendentes para o usuário.

        TODO: implementar com base no model de Invite.
        Ex.: Invite.objects.filter(email=user.email, status='pending')
        """
        return []

    @staticmethod
    def _get_recent_activities(user, limit: int = 10) -> list:
        """Últimas atividades do usuário.

        TODO: implementar com base no model de Activity/AuditLog.
        Ex.: Activity.objects.filter(user=user).order_by('-created_at')[:limit]
        """
        return []

    @staticmethod
    def _get_quick_stats(user) -> dict[str, int]:
        """Contadores rápidos para cards do dashboard.

        TODO: preencher conforme necessidade do template.
        """
        return {
            'total_organizations': 0,
            'pending_invites_count': 0,
            'unread_notifications': 0,
        }
