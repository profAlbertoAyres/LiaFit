from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from account.exceptions import TokenError, TokenExpiredError, TokenAlreadyUsedError, TokenInvalidError
from account.forms.onboarding_form import OrganizationRegistrationForm, SetupPasswordForm
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


def resend_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        OnboardingService.resend_password_token(email, request)
        messages.success(
            request,
            'Se o e-mail estiver cadastrado, enviamos um link.',
        )
        return redirect('auth:login')

    return render(request, 'accounts/auth/password_reset_done.html')


class OrganizationDetailView(BaseDetailView):
    model = Organization
    template_name = "accounts/organizations/detail.html"
    context_object_name = "organization"

    require_tenant = True
    permission_required = "settings.view_organization"
