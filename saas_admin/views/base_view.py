import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
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

class SaaSBaseToggleStatusView(SaaSAdminRequiredMixin, View):

    http_method_names = ["post"]

    model = None
    service_action = None
    fallback_url = None
    pk_url_kwarg = "pk"

    # ──────────────── Hooks customizáveis ────────────────

    def get_object(self):
        """Hook: subclasse pode sobrescrever pra adicionar filtros."""
        if self.model is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} precisa definir 'model'."
            )
        pk = self.kwargs.get(self.pk_url_kwarg)
        return get_object_or_404(self.model, pk=pk)

    def get_service_action(self):
        """Hook: retorna o callable que executa a ação."""
        if self.service_action is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} precisa definir 'service_action'."
            )
        return self.service_action

    def get_fallback_url(self):
        """Hook: URL de fallback caso HTTP_REFERER esteja ausente."""
        if self.fallback_url is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} precisa definir 'fallback_url'."
            )
        return reverse(self.fallback_url)

    def get_message_level(self, action: str) -> int:

        if action == "deactivated":
            return messages.WARNING
        return messages.SUCCESS

    # ──────────────── Fluxo principal ────────────────

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        action_callable = self.get_service_action()

        result = action_callable(instance)

        level = self.get_message_level(result["action"])
        messages.add_message(request, level, result["message"])

        next_url = request.META.get("HTTP_REFERER") or self.get_fallback_url()
        return redirect(next_url)