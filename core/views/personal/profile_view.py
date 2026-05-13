# core/views/personal/profile_view.py
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from core.forms.personal.profile_form import ProfileForm
from core.views.base_view import BaseAuthMixin


class ProfileDetailView(BaseAuthMixin, TemplateView):
    template_name = "core/personal/detail.html"
    require_tenant = False
    permission_required = None


class ProfileEditView(BaseAuthMixin, UpdateView):
    """Edição do perfil pessoal do usuário autenticado."""
    form_class = ProfileForm
    require_tenant = False
    permission_required = None
    template_name = 'core/personal/edit.html'
    success_url = reverse_lazy('personal:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_obj'] = self.request.user
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Não foi possível salvar. Verifique os campos destacados.'
        )
        return super().form_invalid(form)