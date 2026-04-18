# core/views/post_login.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View

from account.models import OrganizationMember


class PostLoginRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        memberships = (
            OrganizationMember.objects
            .filter(user=request.user, is_active=True)
            .select_related('organization')
            .filter(organization__is_active=True)
        )

        orgs = [m.organization for m in memberships]

        # ── SEM ORGS (só cliente, sem membership staff) ──
        if not orgs:
            messages.info(
                request,
                "Você ainda não está vinculado a nenhuma organização."
            )
            return redirect('website:index')

        # ── 1 ORG → direto ──
        if len(orgs) == 1:
            return redirect(
                'tenant:dashboard',
                org_slug=orgs[0].slug,
            )

        # ── N ORGS → última acessada ou primeira ──
        last_slug = request.session.get('last_org_slug')

        # Verifica se a última acessada ainda é válida
        target_org = None
        if last_slug:
            target_org = next(
                (o for o in orgs if o.slug == last_slug),
                None,
            )

        if not target_org:
            target_org = orgs[0]

        # Alerta informando qual org está ativa
        messages.info(
            request,
            f'Você está acessando "{target_org.company_name}". '
            f'Use o seletor no topo para trocar de organização.',
        )

        return redirect(
            'tenant:dashboard',
            org_slug=target_org.slug,
        )
