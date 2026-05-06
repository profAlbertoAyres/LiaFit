"""
Service responsável por calcular as métricas exibidas no
Dashboard do SaaS Admin.

Mantém a view fina e a lógica testável isoladamente.
Segue o mesmo padrão dos outros services do app
(AdminOrganizationService, OnboardingService, etc.).
"""
from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from account.models import Organization, Specialty, User


class SaaSAdminDashboardService:
    """Agrega métricas globais da plataforma para o painel SaaS."""

    # Quantos itens mostrar na tabela "últimas organizações"
    RECENT_ORGS_LIMIT = 5

    # Janela de tempo para "novas organizações"
    NEW_ORGS_WINDOW_DAYS = 30

    # ──────────────── API pública ────────────────

    @classmethod
    def get_metrics(cls) -> dict:
        """
        Retorna o dicionário completo de métricas para o dashboard.

        Returns:
            dict com chaves:
              - total_organizations (int)
              - active_organizations (int)
              - inactive_organizations (int)
              - total_users (int)
              - total_specialties (int)
              - new_orgs_last_30_days (int)
              - recent_organizations (QuerySet[Organization])
        """
        since = timezone.now() - timedelta(days=cls.NEW_ORGS_WINDOW_DAYS)

        return {
            "total_organizations": cls._count_total_organizations(),
            "active_organizations": cls._count_active_organizations(),
            "inactive_organizations": cls._count_inactive_organizations(),
            "total_users": cls._count_active_users(),
            "total_specialties": cls._count_active_specialties(),
            "new_orgs_last_30_days": cls._count_new_orgs_since(since),
            "recent_organizations": cls._get_recent_organizations(),
        }

    # ──────────────── Métricas individuais ────────────────

    @staticmethod
    def _count_total_organizations() -> int:
        return Organization.objects.count()

    @staticmethod
    def _count_active_organizations() -> int:
        return Organization.objects.filter(is_active=True).count()

    @staticmethod
    def _count_inactive_organizations() -> int:
        return Organization.objects.filter(is_active=False).count()

    @staticmethod
    def _count_active_users() -> int:
        return User.objects.filter(is_active=True).count()

    @staticmethod
    def _count_active_specialties() -> int:
        return Specialty.objects.filter(is_active=True).count()

    @staticmethod
    def _count_new_orgs_since(since) -> int:
        return Organization.objects.filter(created_at__gte=since).count()

    @classmethod
    def _get_recent_organizations(cls):
        """Últimas N organizações cadastradas (mais recentes primeiro)."""
        return (
            Organization.objects
            .select_related("owner")
            .order_by("-created_at")[:cls.RECENT_ORGS_LIMIT]
        )
