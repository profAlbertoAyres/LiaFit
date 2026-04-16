from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)


# ─────────────────────────────────────────────
# 🔐 AUTENTICAÇÃO + PERMISSÃO (SaaS)
# ─────────────────────────────────────────────

class BaseAuthMixin(LoginRequiredMixin):
    """
    Mixin que verifica:
    1. Usuário autenticado
    2. Módulo habilitado na organização
    3. Permissão do papel (role) do usuário
    """

    login_url = "account:login"
    permission_required = None
    module_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        ctx = getattr(request, "context", None)

        if not ctx:
            return self._deny("Contexto não encontrado. Faça login novamente.")

        if self.module_required:
            if self.module_required not in ctx.modules and "*" not in ctx.modules:
                return self._deny("Módulo não habilitado para sua organização.")

        if self.permission_required:
            if self.permission_required not in ctx.permissions and "*" not in ctx.permissions:
                return self._deny("Você não tem permissão para acessar esta funcionalidade.")

        return super().dispatch(request, *args, **kwargs)

    def _deny(self, message):
        messages.error(self.request, message)
        return redirect("account:dashboard")


# ─────────────────────────────────────────────
# 🏢 CONTEXTO MULTI-TENANT
# ─────────────────────────────────────────────

class ContextMixin:
    """
    Filtra automaticamente o queryset pela organização
    e pelo profissional do contexto da request.
    """

    def get_ctx(self):
        return getattr(self.request, "context", None)

    def get_organization(self):
        ctx = self.get_ctx()
        if not ctx or not ctx.organization:
            raise PermissionDenied("Organização não encontrada.")
        return ctx.organization

    def get_queryset(self):
        queryset = super().get_queryset()
        ctx = self.get_ctx()

        if not ctx or not ctx.organization:
            return queryset.none()

        model = queryset.model

        if hasattr(model, "organization"):
            queryset = queryset.filter(organization=ctx.organization)

        if hasattr(model, "professional") and ctx.professional:
            queryset = queryset.filter(professional=ctx.professional)

        return queryset


# ─────────────────────────────────────────────
# 📋 LIST
# ─────────────────────────────────────────────

class BaseListView(ContextMixin, BaseAuthMixin, ListView):

    filterset_class = None
    paginate_by = 10
    ordering = None

    def get_filterset(self, queryset):
        if not self.filterset_class:
            return None
        return self.filterset_class(
            self.request.GET or None,
            queryset=queryset,
            request=self.request,
        )

    def get_queryset(self):
        queryset = super().get_queryset()

        filterset = self.get_filterset(queryset)
        if filterset:
            self.filterset = filterset
            queryset = filterset.qs

        order = self.request.GET.get("order_by")
        if order:
            queryset = queryset.order_by(order)
        elif self.ordering:
            queryset = queryset.order_by(self.ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = getattr(self, "filterset", None)
        return context


# ─────────────────────────────────────────────
# ➕ CREATE
# ─────────────────────────────────────────────

class BaseCreateView(ContextMixin, BaseAuthMixin, CreateView):

    def form_valid(self, form):
        organization = self.get_organization()

        if hasattr(form.instance, "organization"):
            form.instance.organization = organization

        return super().form_valid(form)


# ─────────────────────────────────────────────
# ✏️ UPDATE
# ─────────────────────────────────────────────

class BaseUpdateView(ContextMixin, BaseAuthMixin, UpdateView):

    def form_valid(self, form):
        # Garante que a organização não seja alterada
        organization = self.get_organization()

        if hasattr(form.instance, "organization"):
            form.instance.organization = organization

        return super().form_valid(form)


# ─────────────────────────────────────────────
# 🔍 DETAIL
# ─────────────────────────────────────────────

class BaseDetailView(ContextMixin, BaseAuthMixin, DetailView):
    pass


# ─────────────────────────────────────────────
# 🗑️ DELETE
# ─────────────────────────────────────────────

class BaseDeleteView(ContextMixin, BaseAuthMixin, DeleteView):

    def get_success_url(self):
        if not self.success_url:
            raise ValueError("Defina 'success_url' na sua view de exclusão.")
        return self.success_url
