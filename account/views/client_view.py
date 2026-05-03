from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from account.exceptions import (
    TokenError, TokenExpiredError, TokenAlreadyUsedError, TokenInvalidError,
)
from account.filters.client_filter import OrganizationClientFilter
from account.forms.client_form import ClientCreateForm, ClientUpdateForm
from account.forms.onboarding_form import AcceptInviteForm
from account.models import OnboardingToken, OrganizationClient
from account.services.client_service import ClientService
from account.services.onboarding_service import OnboardingService
from account.services.token_service import TokenService
from core.views.base_view import (
    BaseListView, BaseDetailView, BaseFormView, BaseUpdateView, BaseDeleteView,
)


# ──────────────── CRUD ────────────────

class ClientListView(BaseListView):
    model = OrganizationClient
    template_name = "accounts/client/list.html"
    context_object_name = "clients"

    require_tenant = True
    permission_required = "account.view_client"

    paginate_by = 10
    filterset_class = OrganizationClientFilter

    queryset = None

    def get_queryset(self):
        self.queryset = (
            OrganizationClient.all_objects
            .filter(organization=self.request.context.organization)
            .select_related('user__user', 'organization', 'created_by')
        )
        # 2) Deixa o BaseListView aplicar filterset + ordering
        return super().get_queryset()

class ClientDetailView(BaseDetailView):
    model = OrganizationClient
    template_name = "accounts/client/detail.html"
    context_object_name = "client"

    require_tenant = True
    permission_required = "account.view_client"

    def get_queryset(self):
        return super().get_queryset().select_related('user__user', 'organization')


class ClientCreateView(BaseFormView):
    form_class = ClientCreateForm
    template_name = "accounts/client/create.html"

    require_tenant = True
    permission_required = "account.add_client"

    def form_valid(self, form):
        try:
            org_client = ClientService.create_client(
                organization=self.request.context.organization,
                data=form.cleaned_data,
                request=self.request,
                created_by=self.request.user,
            )
        except ValueError as e:
            form.add_error('email', str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Cliente cadastrado! E-mail enviado para {org_client.user.user.email}.",
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'tenant:client_list',
            kwargs={'org_slug': self.request.context.organization.slug},
        )


class ClientUpdateView(BaseUpdateView):
    model = OrganizationClient
    form_class = ClientUpdateForm
    template_name = "accounts/client/create.html"

    require_tenant = True
    permission_required = "account.change_client"

    def get_initial(self):
        initial = super().get_initial()
        user = self.object.user.user
        initial.update({
            'fullname': user.fullname,
            'email': user.email,
            'phone': user.phone,
            'cpf': user.cpf,
            'objective': self.object.objective,
            'notes': self.object.notes,
        })
        return initial

    def form_valid(self, form):
        ClientService.update_client(self.object, form.cleaned_data)
        messages.success(self.request, "Cliente atualizado com sucesso!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'tenant:client_list',
            kwargs={'org_slug': self.request.context.organization.slug},
        )


class ClientArchiveView(BaseDeleteView):
    """Soft delete (archived_at)."""
    model = OrganizationClient
    template_name = "accounts/client/archive_confirm.html"

    require_tenant = True
    permission_required = "account.delete_client"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        ClientService.archive_client(self.object)
        messages.success(request, "Cliente arquivado com sucesso.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'tenant:client_list',
            kwargs={'org_slug': self.request.context.organization.slug},
        )


# ──────────────── ACCEPT INVITE (público) ────────────────

@method_decorator(never_cache, name='dispatch')
class AcceptClientInviteView(View):
    template_name = 'accounts/auth/accept_client_invite.html'
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def _get_token_or_invalid(self, request, token):
        try:
            token_obj = TokenService.get_valid_token(
                token,
                expected_purpose=OnboardingToken.Purpose.CLIENT_ACTIVATION,
            )
        except TokenError as e:
            response = render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )
            return None, response
        return token_obj, None

    def get(self, request, token):
        token_obj, invalid = self._get_token_or_invalid(request, token)
        if invalid:
            return invalid

        return render(request, self.template_name, {
            "form": AcceptInviteForm(),
            "token": token,
            "invited_user": token_obj.user,
            "organization": token_obj.organization,
        })

    def post(self, request, token):
        token_obj, invalid = self._get_token_or_invalid(request, token)
        if invalid:
            return invalid

        form = AcceptInviteForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "token": token,
                "invited_user": token_obj.user,
                "organization": token_obj.organization,
            })

        try:
            OnboardingService.activate_client(
                token_str=token,
                password=form.cleaned_data['password1'],
                request=request,
            )
        except TokenExpiredError:
            messages.error(request, "Link expirado. Solicite um novo.")
            return redirect("auth:login")
        except TokenAlreadyUsedError:
            messages.info(request, "Este convite já foi aceito. Faça login.")
            return redirect("auth:login")
        except TokenInvalidError:
            return render(
                request, self.invalid_template_name,
                {"error_message": "Token inválido."}, status=400,
            )

        messages.success(
            request,
            f"Bem-vindo(a) à {token_obj.organization.company_name}! 🎉",
        )
        return redirect("master:dashboard")
