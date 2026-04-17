from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from account.forms import OrganizationRegistrationForm


class OrganizationRegisterView(FormView):
    template_name = 'accounts/auth/register.html'
    form_class = OrganizationRegistrationForm

    success_url = reverse_lazy('auth:register')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'Conta criada com sucesso! Verifique seu e-mail para definir sua senha e acessar o sistema.'
                         )
        return super().form_valid(form)


class SetupPasswordView(View):
    template_name = 'accounts/auth/setup_password.html'
    invalid_template_name = 'accounts/auth/setup_password_invalid.html'

    def get(self, request, token):
        token_obj = ActivationService.get_valid_token(token)
        if not token_obj:
            return render(request, self.invalid_template, status=400)

        return render(request, self.template_name, {
            "form": SetupPasswordForm(),
            "email": token_obj.user.email,
        })

class LoginView(FormView):
    pass
