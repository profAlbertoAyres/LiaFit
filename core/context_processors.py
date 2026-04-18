from django.conf import settings
from account.models import OrganizationMember


def global_settings(request):
    """Injeta variáveis globais do settings nos templates."""
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'Lia Linda'),
    }


def tenant_context(request):
    """
    Injeta dados do tenant nos templates.
    Trabalha junto com o SaaSContextMiddleware.
    """
    if not hasattr(request, 'context'):
        return {}

    if not request.user.is_authenticated:
        return {}

    # Org e membership vindos do middleware
    current_org = getattr(request.context, 'organization', None)
    current_membership = getattr(request.context, 'membership', None)

    # Busca todas as orgs ativas do usuário (para o seletor)
    user_memberships = (
        OrganizationMember.objects
        .filter(user=request.user, is_active=True)
        .select_related('organization')
        .only(
            'id', 'is_active',
            'organization__id',
            'organization__company_name',
            'organization__slug',
            'organization__is_active',
        )
    )

    user_organizations = [
        m.organization
        for m in user_memberships
        if m.organization.is_active
    ]

    return {
        'current_organization': current_org,
        'current_membership': current_membership,
        'user_organizations': user_organizations,
        'show_org_selector': len(user_organizations) > 1,
    }
