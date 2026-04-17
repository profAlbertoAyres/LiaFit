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

# 🔐 AUTENTICAÇÃO + PERMISSÃO (SaaS v2.2)
class BaseAuthMixin(LoginRequiredMixin):
    """
    Mixin que verifica:
    1. Usuário autenticado
    2. Membro ativo na Organização atual
    3. Permissão do papel (Role) do membro
    """

    login_url = "account:login"
    permission_required = None

    # module_required = None # Pode ser usado caso você implemente Planos de Assinatura no futuro

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Na v2.2, assumimos que você tem um Middleware (ou no próprio request)
        # que injeta request.tenant (Organization) e request.member (OrganizationMember)
        tenant = getattr(request, "tenant", None)
        member = getattr(request, "member", None)

        if not tenant or not member:
            return self._deny("Contexto de organização não encontrado. Faça login novamente.")

        # Verifica permissões baseadas no Role do membro
        if self.permission_required:
            member_permissions = member.role.permissions if member.role else []

            # Se não for admin e não tiver a permissão específica
            if not member.is_admin and self.permission_required not in member_permissions:
                return self._deny("Você não tem permissão para acessar esta funcionalidade.")

        return super().dispatch(request, *args, **kwargs)

    def _deny(self, message):
        messages.error(self.request, message)
        return redirect("core:dashboard")  # Ajuste para a rota do seu dashboard

# 🏢 CONTEXTO MULTI-TENANT (SaaS v2.2)
class ContextMixin:
    """
    Filtra automaticamente o queryset pela organização
    e lida com a injeção do tenant nos forms.
    """

    def get_tenant(self):
        tenant = getattr(self.request, "tenant", None)
        if not tenant:
            raise PermissionDenied("Organização não encontrada.")
        return tenant

    def get_member(self):
        return getattr(self.request, "member", None)

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        member = getattr(self.request, "member", None)

        if not tenant:
            return queryset.none()

        model = queryset.model

        # 1. Filtra sempre pela Organização (Isolamento de Tenant)
        if hasattr(model, "organization") or any(f.name == 'organization' for f in model._meta.fields):
            queryset = queryset.filter(organization=tenant)

        # 2. Se o modelo tiver um campo 'member' (ex: Tarefas, Clientes de um instrutor específico)
        # e o usuário atual NÃO for admin, filtramos apenas para o que pertence a ele.
        if hasattr(model, "member") and member and not member.is_admin:
            queryset = queryset.filter(member=member)

        return queryset

    def get_form_kwargs(self):
        """Injeta o tenant e o membro nos forms que herdam de BaseModelForm"""
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = getattr(self.request, "tenant", None)
        kwargs['member'] = getattr(self.request, "member", None)  # antigo 'professional'
        return kwargs

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

# ➕ CREATE
class BaseCreateView(ContextMixin, BaseAuthMixin, CreateView):
    def form_valid(self, form):
        tenant = self.get_tenant()

        # Garante que o registro pertença à organização atual
        if hasattr(form.instance, "organization"):
            form.instance.organization = tenant

        return super().form_valid(form)

# ✏️ UPDATE
class BaseUpdateView(ContextMixin, BaseAuthMixin, UpdateView):
    def form_valid(self, form):
        tenant = self.get_tenant()

        # Impede que um update malicioso mude a organização do registro
        if hasattr(form.instance, "organization"):
            form.instance.organization = tenant

        return super().form_valid(form)

# 🔍 DETAIL & 🗑️ DELETE
class BaseDetailView(ContextMixin, BaseAuthMixin, DetailView):
    pass


class BaseDeleteView(ContextMixin, BaseAuthMixin, DeleteView):
    def get_success_url(self):
        if not self.success_url:
            raise ValueError("Defina 'success_url' na sua view de exclusão.")
        return self.success_url

