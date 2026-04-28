from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class ClientListView(LoginRequiredMixin, TemplateView):
    template_name = "account/client_list.html"
