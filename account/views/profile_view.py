from django.views.generic import TemplateView

from core.views.base_view import BaseAuthMixin


class ProfileView(BaseAuthMixin, TemplateView):
    template_name = "accounts/member/profile.html"
    require_tenant = False
    permission_required = None
