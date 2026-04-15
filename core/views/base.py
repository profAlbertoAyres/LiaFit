from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, DetailView, DeleteView, ListView


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class BaseAuthMixin(LoginRequiredMixin):

    permission_required = None
    module_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        ctx = getattr(request, "context", None)

        if not ctx:
            return self.handle_no_permission()

        # 1. CHECK MODULE ACCESS
        if self.module_required:
            if self.module_required not in ctx.modules and "*" not in ctx.modules:
                return self._deny("Módulo não habilitado para sua organização.")

        # 2. CHECK PERMISSIONS
        if self.permission_required:
            if self.permission_required not in ctx.permissions and "*" not in ctx.permissions:
                return self._deny("Você não tem permissão para acessar esta funcionalidade.")

        return super().dispatch(request, *args, **kwargs)

    def _deny(self, message):
        messages.error(self.request, message)
        return redirect("account:dashboard")

    def handle_no_permission(self):
        return self._deny("Acesso negado.")

from django.core.exceptions import PermissionDenied

class ContextMixin:

    def get_ctx(self):
        return getattr(self.request, "context", None)

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
            self.filterset = filterset  # 🔥 FIX
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

from django.core.exceptions import PermissionDenied

class BaseCreateView(BaseAuthMixin, CreateView):

    def get_ctx(self):
        return getattr(self.request, "context", None)

    def form_valid(self, form):
        ctx = self.get_ctx()

        if not ctx or not ctx.organization:
            raise PermissionDenied("Organização não encontrada")

        if hasattr(form.instance, "organization"):
            form.instance.organization = ctx.organization

        return super().form_valid(form)

class BaseUpdateView(ContextMixin, BaseAuthMixin, UpdateView):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        ctx = self.get_ctx()

        kwargs["professional"] = getattr(ctx, "professional", None)
        kwargs["tenant"] = getattr(ctx, "organization", None)

        return kwargs


class BaseDetailView(ContextMixin, BaseAuthMixin, DetailView):
    pass


class BaseDeleteView(ContextMixin, BaseAuthMixin, DeleteView):

    success_url = None

    def get_success_url(self):
        if not self.success_url:
            raise ValueError("Defina 'success_url' na sua view de exclusão")
        return self.success_url