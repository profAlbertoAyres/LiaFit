from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from account.models import OrganizationMember
from core.services.post_login import resolve_post_login_redirect


class PostLoginRedirectView(LoginRequiredMixin, View):
    require_tenant = False
    def get(self, request):
        last_org_slug = request.session.get('last_org_slug')
        redirect_url, msg = resolve_post_login_redirect(request.user, last_org_slug)
        if msg:
            messages.info(request, msg)

        # 4. Redireciona para a URL definida pelo Service
        return redirect(redirect_url)

