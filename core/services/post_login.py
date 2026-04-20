from django.urls import reverse
from account.models import OrganizationMember

# Removi a função get_user_companies que não estava sendo usada e usava `user.empresas` em vez de OrganizationMember

def resolve_post_login_redirect(user, last_org_slug=None):
    if user.is_superuser:
        url = reverse('core:dashboard') # Ou tenant:dashboard se ele for adm de um
        msg = "Você acessou como super usuário."
        return url, msg

    # Busca as organizações que o usuário é membro
    memberships = (
        OrganizationMember.objects
        .filter(user=user, is_active=True)
        .select_related('organization')
        .filter(organization__is_active=True)
    )

    orgs = [m.organization for m in memberships]

    # SEM ORG (Cliente Global)
    if not orgs:
        url = reverse('core:dashboard')
        msg = "Você acessou seu painel pessoal."
        return url, msg

    # UMA ÚNICA ORG
    if len(orgs) == 1:
        url = reverse('tenant:dashboard', kwargs={'org_slug': orgs[0].slug})
        # CORREÇÃO: Faltava o nome da empresa aqui
        msg = f'Você está acessando "{orgs[0].company_name}".'
        return url, msg

    # MÚLTIPLAS ORGS
    target_org = None
    if last_org_slug:
        target_org = next((o for o in orgs if o.slug == last_org_slug), None)

    if not target_org:
        target_org = orgs[0]

    url = reverse('tenant:dashboard', kwargs={'org_slug': target_org.slug})
    msg = (
        f'Você está acessando "{target_org.company_name}". '
        f'Use o seletor no topo para trocar de organização.'
    )
    return url, msg
