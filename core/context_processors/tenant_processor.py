# core/context_processors/tenant_processor.py
"""
Context processor de tenant (organização atual).

Injeta no template:
    - current_organization: organização ativa do request (vem do middleware)
    - current_membership: vínculo do usuário com a organização atual
    - user_organizations: lista de orgs ativas do usuário (para o seletor)
    - show_org_selector: True se o usuário tem mais de uma org ativa

Depende de `request.context` populado pelo SaaSContextMiddleware.
"""
from account.models import OrganizationMember
from core.services.space_service import get_user_spaces


def tenant_context(request):
    if not hasattr(request, 'context'):
        return {}

    if not request.user.is_authenticated:
        return {}

    # Org e membership vindos do middleware
    current_org = getattr(request.context, 'organization', None)
    current_membership = getattr(request.context, 'membership', None)
    spaces = get_user_spaces(request.user)


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

    return {
        'current_organization': current_org,
        'current_membership': current_membership,
        'user_has_multiple_spaces': len(spaces) >= 2,

    }
