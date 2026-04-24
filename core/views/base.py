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


# ─── AUTENTICAÇÃO + PERMISSÃO ────────────────────────────────

class BaseAuthMixin(LoginRequiredMixin):
    """
    Exige usuário autenticado + (opcionalmente) tenant + permissão RBAC.

    Atributos:
        require_tenant: bool  — exige org na URL (default: True)
        permission_required: str | tuple[str] | None
            - str   → exige essa única permissão
            - tuple → AND: exige TODAS
            - None  → não checa permissão (só auth + tenant)
        permission_required_any: tuple[str] | None
            - tuple → OR: basta ter UMA
    """

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

    # ─── Helpers privados ────────────────────────────────────

    def _check_tenant_access(self, request):
        """Retorna um redirect se negado, ou None se OK."""
        ctx = getattr(request, 'context', None)

        # Superuser: só precisa de org na URL
        if request.user.is_superuser:
            if not getattr(ctx, 'organization', None):
                return self._deny("Organização não encontrada na URL.")
            return None

        # Usuário comum: exige contexto com membership
        if not ctx or not getattr(ctx, 'membership', None):
            return self._deny(
                "Contexto de organização não encontrado. Faça login novamente."
            )

        # RBAC
        if not self._has_required_permission(ctx):
            return self._deny(
                "Você não tem permissão para acessar esta funcionalidade."
            )

        return None

    def _has_required_permission(self, ctx) -> bool:
        """Delega a decisão pro MemberContext."""
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

# ─── CONTEXTO MULTI-TENANT ───────────────────────────────────

class ContextMixin:

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

        # 1. Filtra sempre pela Organização (isolamento de tenant)
        if hasattr(model, 'organization') or any(
            f.name == 'organization' for f in model._meta.fields
        ):
            queryset = queryset.filter(organization=tenant)

        # 2. Se o modelo tem campo 'member' e o usuário NÃO é admin/superuser,
        #    filtra apenas registros que pertencem a ele.
        if (
            hasattr(model, 'member')
            and membership
            and not self.request.user.is_superuser
            and not (member_ctx and member_ctx.is_admin())
        ):
            queryset = queryset.filter(member=membership)

        return queryset

    def get_form_kwargs(self):
        """Injeta tenant e membership nos forms."""
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = getattr(self.request.context, 'organization', None)
        kwargs['membership'] = getattr(self.request.context, 'membership', None)
        return kwargs

    @staticmethod
    def _is_admin(membership):
        """Verifica se o membro tem role de admin/owner."""
        roles = getattr(membership, 'roles', None)
        if roles is None:
            return False
        if callable(getattr(roles, 'all', None)):
            return roles.filter(slug__in=['owner', 'admin']).exists()
        return any(r.slug in ('owner', 'admin') for r in roles)


# ─── VIEWS CONCRETAS ─────────────────────────────────────────

# 📋 LIST
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


# ➕ CREATE
class BaseCreateView(ContextMixin, BaseAuthMixin, CreateView):
    def form_valid(self, form):
        tenant = self.get_tenant()
        if any(f.name == 'organization' for f in form.instance._meta.fields):
            form.instance.organization = tenant

        return super().form_valid(form)


# ✏️ UPDATE
class BaseUpdateView(ContextMixin, BaseAuthMixin, UpdateView):
    def form_valid(self, form):
        tenant = self.get_tenant()
        if any(f.name == 'organization' for f in form.instance._meta.fields):
            form.instance.organization = tenant

        return super().form_valid(form)

# 🔍 DETAIL
class BaseDetailView(ContextMixin, BaseAuthMixin, DetailView):
    pass


# 🗑️ DELETE
class BaseDeleteView(ContextMixin, BaseAuthMixin, DeleteView):
    def get_success_url(self):
        if not self.success_url:
            raise ValueError("Defina 'success_url' na sua view de exclusão.")
        return self.success_url
