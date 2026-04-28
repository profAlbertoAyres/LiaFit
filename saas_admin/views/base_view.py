import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404

from core.services.permission_service import is_saas_staff

logger = logging.getLogger(__name__)


class SaaSAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    raise_exception = True

    def test_func(self) -> bool:
        user = self.request.user

        if not user.is_authenticated:
            return False

        if not user.is_active:
            return False

        return is_saas_staff(user)

    def handle_no_permission(self):

        user = self.request.user
        user_repr = (
            f"user_id={user.pk}" if user.is_authenticated else "anonymous"
        )

        logger.warning(
            "Acesso negado ao SaaS Admin: %s tentou acessar %s",
            user_repr,
            self.request.path,
        )

        raise Http404("Página não encontrada.")
