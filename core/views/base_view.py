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
    FormView,
)


# ─── AUTENTICAÇÃO + PERMISSÃO ────────────────────────────────

class BaseAuthMixin(LoginRequiredMixin):

    require_tenant = True
    permission_required = None
    permission_required_any = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.require_tenant:
            denied = self._check_tenant_access(request)
            if denied:
                return denied

        return super().dispatch(request, *args, **kwargs)

    def _check_tenant_access(self, request):
        ctx = getattr(request, 'context', None)

        if request.user.is_superuser:
            if not getattr(ctx, 'organization', None):
                return self._deny("Organização não encontrada na URL.")
            return None

        if not ctx or not getattr(ctx, 'membership', None):
            return self._deny(
                "Contexto de organização não encontrado. Faça login novamente."
            )

        if not self._has_required_permission(ctx):
            return self._deny(
                "Você não tem permissão para acessar esta funcionalidade."
            )

        return None

    def _has_required_permission(self, ctx) -> bool:
        if self.permission_required:
            required = self.permission_required
            if isinstance(required, str):
                return ctx.has_permission(required)
            return ctx.has_all_permissions(*required)

        if self.permission_required_any:
            return ctx.has_any_permission(*self.permission_required_any)

        return True

    def _deny(self, message):
        messages.error(self.request, message)
        return redirect("master:dashboard")


# ─── CONTEXTO DE TENANT ──────────────────────────────────────

class TenantContextMixin:
    """Helpers de tenant. Seguro em qualquer CBV (incluindo TemplateView)."""

    def get_tenant(self):
        if getattr(self, 'require_tenant', True) is False:
            return None
        ctx = getattr(self.request, 'context', None)
        tenant = getattr(ctx, 'organization', None)
        if not tenant:
            raise PermissionDenied("Organização não encontrada.")
        return tenant

    def get_membership(self):
        ctx = getattr(self.request, 'context', None)
        return getattr(ctx, 'membership', None)


class ContextMixin(TenantContextMixin):
    """Filtros multi-tenant em queryset/form. Só usar em CBVs de modelo."""

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, 'require_tenant', True) is False:
            return queryset

        ctx = self.request.context
        tenant = getattr(ctx, 'organization', None)
        membership = getattr(ctx, 'membership', None)
        member_ctx = getattr(ctx, 'member_ctx', None)

        if not tenant:
            return queryset.none()

        model = queryset.model

        if hasattr(model, 'organization') or any(
            f.name == 'organization' for f in model._meta.fields
        ):
            queryset = queryset.filter(organization=tenant)

        if (
            hasattr(model, 'member')
            and membership
            and not self.request.user.is_superuser
            and not (member_ctx and member_ctx.is_admin())
        ):
            queryset = queryset.filter(member=membership)

        return queryset

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.get_tenant()
        kwargs['membership'] = self.get_membership()
        return kwargs


# ─── BASE VIEWS ──────────────────────────────────────────────

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

        order = self.request.GET.get('order_by')
        if order:
            queryset = queryset.order_by(order)
        elif self.ordering:
            queryset = queryset.order_by(self.ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = getattr(self, 'filterset', None)
        return context


class BaseCreateView(ContextMixin, BaseAuthMixin, CreateView):
    def form_valid(self, form):
        tenant = self.get_tenant()
        if tenant and any(f.name == 'organization' for f in form.instance._meta.fields):
            form.instance.organization = tenant
        return super().form_valid(form)


class BaseUpdateView(ContextMixin, BaseAuthMixin, UpdateView):
    def form_valid(self, form):
        tenant = self.get_tenant()
        if tenant and any(f.name == 'organization' for f in form.instance._meta.fields):
            form.instance.organization = tenant
        return super().form_valid(form)


class BaseDetailView(ContextMixin, BaseAuthMixin, DetailView):
    pass


class BaseDeleteView(ContextMixin, BaseAuthMixin, DeleteView):
    def get_success_url(self):
        if not self.success_url:
            raise ValueError("Defina 'success_url' na sua view de exclusão.")
        return self.success_url


class BaseFormView(TenantContextMixin, BaseAuthMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.get_tenant()
        kwargs['membership'] = self.get_membership()
        return kwargs
