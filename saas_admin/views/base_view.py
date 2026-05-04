import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView

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


class SaaSBaseListView(SaaSAdminRequiredMixin, ListView):
    """Base para listagens no painel SaaS com suporte a filtros (django-filter)."""
    paginate_by = 10
    filterset_class = None  # Receberá a classe de filtro, se houver

    def get_queryset(self):
        # 1. Pega a query original (ex: Organization.objects.all())
        queryset = super().get_queryset()

        # 2. Se houver uma classe de filtro definida, aplica na query
        if self.filterset_class:
            self.filterset = self.filterset_class(
                self.request.GET or None,
                queryset=queryset,
                request=self.request,
            )
            queryset = self.filterset.qs

        return queryset

    def get_context_data(self, **kwargs):
        # 3. Manda o filtro para o templates para podermos renderizar o formulário de busca
        context = super().get_context_data(**kwargs)
        if getattr(self, 'filterset', None):
            context['filter'] = self.filterset
        return context


class SaaSBaseDetailView(SaaSAdminRequiredMixin, DetailView):
    """Base para detalhes de um registro no painel SaaS."""
    pass


class SaaSBaseCreateView(SaaSAdminRequiredMixin, CreateView):
    """Base para criação de registros no painel SaaS."""
    pass


class SaaSBaseUpdateView(SaaSAdminRequiredMixin, UpdateView):
    """Base para edição de registros no painel SaaS."""
    pass

class SaaSBaseFormView(SaaSAdminRequiredMixin, FormView):
    """Base para formulários de ação (não-CRUD direto) no painel SaaS."""
    pass