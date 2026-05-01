from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView

from account.exceptions import TokenError, TokenExpiredError, TokenAlreadyUsedError, TokenInvalidError
from account.forms.onboarding_form import OrganizationRegistrationForm, SetupPasswordForm, AcceptInviteForm, \
    PasswordResetConfirmForm, PasswordResetRequestForm
from account.models import OnboardingToken, Organization
from account.services.onboarding_service import OnboardingService
from account.services.token_service import TokenService
from core.views import BaseDetailView


class OrganizationRegisterView(FormView):
    template_name = 'accounts/auth/register.html'
    form_class = OrganizationRegistrationForm
    success_url = reverse_lazy('auth:register_success')

    def form_valid(self, form):
        if getattr(form, "email_already_exists", False):
            existing = getattr(form, "_existing_user", None)
            return self.render_to_response(self.get_context_data(
                form=form,
                show_email_exists_modal=True,
                existing_is_active=bool(existing and existing.is_active),
            ))

        form.save(request=self.request)

        if form.cleaned_data.get("confirm_existing"):
            messages.success(
                self.request,
                f'Empresa "{form.cleaned_data["company_name"]}" cadastrada e '
                'vinculada à sua conta. Verifique seu e-mail para ativá-la.'
            )
        else:
            messages.success(
                self.request,
                'Empresa cadastrada com sucesso! Verifique seu e-mail '
                'para definir sua senha e acessar o sistema.'
            )
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class ActivateOrganizationView(View):
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def get(self, request, token):
        try:
            user, organization = OnboardingService.activate_organization_by_token(
                token_str=token,
                request=request,
            )
        except TokenExpiredError:
            messages.error(request, "Link de ativação expirado. Solicite um novo cadastro.")
            return redirect("auth:login")
        except TokenAlreadyUsedError:
            messages.info(request, "Esta empresa já foi ativada. Faça login.")
            return redirect("auth:login")
        except (TokenInvalidError, TokenError) as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        messages.success(
            request,
            f"Empresa '{organization.company_name}' ativada com sucesso! 🎉"
        )
        return redirect("master:dashboard")

@method_decorator(never_cache, name='dispatch')
class SetupPasswordView(View):
    template_name = 'accounts/auth/setup_password.html'
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def get(self, request, token):
        try:
            token_obj = TokenService.get_valid_token(
                token,
                expected_purpose=OnboardingToken.Purpose.ONBOARDING,
            )
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        return render(request, self.template_name, {
            "form": SetupPasswordForm(),
            "email": token_obj.user.email,
            "token": token,
        })

    def post(self, request, token):
        try:
            token_obj = TokenService.get_valid_token(
                token,
                expected_purpose=OnboardingToken.Purpose.ONBOARDING,
            )
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {'error_message': str(e)},
                status=400,
            )
        form = SetupPasswordForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    'form': form,
                    'email': token_obj.user.email,
                    'token': token,
                },
            )
        try:
            user = form.save(token=token, request=request)
        except TokenExpiredError:
            messages.error(request, "Link expirado. Solicite um novo.")
            return redirect("auth:login")
        except TokenAlreadyUsedError:
            messages.info(request, "Esta conta já foi ativada. Faça login.")
            return redirect("auth:login")
        except TokenInvalidError:
            return render(request, self.invalid_template_name,
                {'error_message': 'Token inválido.'}, status=400)

        messages.success(request, f"Bem-vindo(a), {user.email}!")
        return redirect("master:dashboard")

class RegisterSuccess(TemplateView):
    template_name = 'accounts/auth/register_success.html'

class PasswordResetRequestView(View):
    """
    GET  → exibe formulário "esqueci minha senha"
    POST → dispara e-mail (silencioso, anti-enumeration) e redireciona pro login
    """
    template_name = 'accounts/auth/password_reset_request.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = (request.POST.get('email') or '').strip()
        OnboardingService.resend_password_reset(email, request)
        messages.success(
            request,
            'Se o e-mail estiver cadastrado, enviamos um link para redefinir sua senha.',
        )
        return redirect('auth:login')


@method_decorator(never_cache, name='dispatch')
class PasswordResetConfirmView(View):
    template_name = 'accounts/auth/password_reset_confirm.html'
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def get(self, request, token):
        try:
            token_obj = TokenService.get_valid_token(
                token,
                expected_purpose=OnboardingToken.Purpose.RESET_PASSWORD,
            )
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        return render(request, self.template_name, {
            "form": PasswordResetConfirmForm(),
            "email": token_obj.user.email,
            "token": token,
        })

    def post(self, request, token):
        try:
            token_obj = TokenService.get_valid_token(
                token,
                expected_purpose=OnboardingToken.Purpose.RESET_PASSWORD,
            )
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        form = PasswordResetConfirmForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "email": token_obj.user.email,
                "token": token,
            })

        try:
            user = form.save(token=token, request=request)
        except TokenExpiredError:
            messages.error(request, "Link expirado. Solicite um novo.")
            return redirect("auth:password_reset_request")
        except TokenAlreadyUsedError:
            messages.info(request, "Este link já foi utilizado. Faça login.")
            return redirect("auth:login")
        except TokenInvalidError:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": "Token inválido."},
                status=400,
            )

        messages.success(request, "Senha redefinida com sucesso! 🎉")
        return redirect("master:dashboard")



class OrganizationDetailView(BaseDetailView):
    model = Organization
    template_name = "accounts/organizations/detail.html"
    context_object_name = "organization"

    require_tenant = True
    permission_required = "settings.view_organization"

    def get_object(self, queryset=None):
        return self.request.context.organization


@method_decorator(never_cache, name='dispatch')
class AcceptInviteView(View):
    template_name = 'accounts/auth/accept_invite.html'
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def get(self, request, token):
        try:
            context = OnboardingService.get_invite_context(token)
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        return render(request, self.template_name, {
            "form": AcceptInviteForm(),
            "token": token,
            **context,
        })

    def post(self, request, token):
        try:
            context = OnboardingService.get_invite_context(token)
        except TokenError as e:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": str(e)},
                status=400,
            )

        form = AcceptInviteForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "token": token,
                **context,
            })

        try:
            form.save(token=token, request=request)
        except TokenExpiredError:
            messages.error(request, "Link de convite expirado. Solicite um novo.")
            return redirect("auth:login")
        except TokenAlreadyUsedError:
            messages.info(request, "Este convite já foi aceito. Faça login.")
            return redirect("auth:login")
        except TokenInvalidError:
            return render(
                request,
                self.invalid_template_name,
                {"error_message": "Token inválido."},
                status=400,
            )

        messages.success(
            request,
            f"Bem-vindo(a) à {context['organization'].company_name}! 🎉"
        )
        return redirect("master:dashboard")


@method_decorator(never_cache, name='dispatch')
class PasswordResetRequestView(View):
    """
    GET  → exibe formulário "esqueci minha senha"
    POST → dispara e-mail (silencioso, anti-enumeration) e redireciona pro login
    """
    template_name = 'accounts/auth/password_reset_request.html'

    def get(self, request):
        return render(request, self.template_name, {
            "form": PasswordResetRequestForm(),
        })

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)

        # 🛡️ Anti-enumeration: mesmo se o form for inválido,
        # mostramos a mensagem de sucesso genérica.
        # Mas só disparamos o e-mail se o formato for válido.
        if form.is_valid():
            email = form.get_normalized_email()
            OnboardingService.resend_password_reset(email, request)

        messages.success(
            request,
            'Se o e-mail estiver cadastrado, enviamos um link para redefinir sua senha.',
        )
        return redirect('auth:login')