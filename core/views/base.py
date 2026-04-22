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
    require_tenant = True  # <--- Por padrão, toda view EXIGE uma clínica na URL!
    permission_required = None
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.require_tenant:
            ctx = getattr(request, 'context', None)
            organization = getattr(ctx, 'organization', None)
            membership = getattr(ctx, 'membership', None)

            # ── Superuser: bypass de membership e RBAC ──
            # if request.user.is_superuser:
            #     if not organization:
            #         return self._deny(
            #             "Organização não encontrada na URL."
            #         )
            #     # Superuser não precisa de membership — acesso total
            #     return super().dispatch(request, *args, **kwargs)
            #
            # # ── Usuário comum: exige org + membership ──
            # if not organization or not membership:
            #     return self._deny(
            #         "Contexto de organização não encontrado. "
            #         "Faça login novamente."
            #     )

            # Verifica permissão RBAC
            if self.permission_required:
                permissions = getattr(ctx, 'permissions', [])
                if self.permission_required not in permissions:
                    return self._deny(
                        "Você não tem permissão para acessar esta funcionalidade."
                    )

        return super().dispatch(request, *args, **kwargs)

    def _deny(self, message):
        messages.error(self.request, message)
        return redirect("core:dashboard")


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
        tenant = getattr(self.request.context, 'organization', None)
        membership = getattr(self.request.context, 'membership', None)

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
            and not self._is_admin(membership)
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
