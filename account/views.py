from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

from account.exceptions import TokenError, TokenExpiredError, TokenAlreadyUsedError, TokenInvalidError
from account.forms.auth import OrganizationRegistrationForm, SetupPasswordForm
from account.models import OnboardingToken
from account.services.onboarding_service import OnboardingService
from account.services.token_service import TokenService


class OrganizationRegisterView(FormView):
    template_name = 'accounts/auth/register.html'
    form_class = OrganizationRegistrationForm
    success_url = reverse_lazy('auth:register_success')

    def form_valid(self, form):
        form.save(request=self.request)
        messages.success(
            self.request, 'Conta criada com sucesso! Verifique seu e-mail para definir sua senha e acessar o sistema.'
                         )
        return super().form_valid(form)


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
        return redirect("core:dashboard")


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



