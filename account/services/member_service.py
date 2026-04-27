import logging

from django.db import transaction

from account.services.onboarding_service import OnboardingService
from account.services.organization_service import OrganizationService
from account.services.professional_service import ProfessionalService
from account.services.user_service import UserService

logger = logging.getLogger(__name__)


class MemberService:

    USER_FIELDS = ('fullname', 'phone', 'gender', 'cpf', 'birth_date')
    MEMBERSHIP_FIELDS = ('remuneration_type', 'joined_at', 'job_title')

    @staticmethod
    @transaction.atomic
    def create_member(organization, data, request=None):
        user = UserService.get_or_create_user(
            email=data['email'],
            extra_fields={
                **{k: data[k] for k in MemberService.USER_FIELDS if data.get(k)},
                'is_active': True,
            },
        )

        membership = OrganizationService.add_member(
            user=user,
            organization=organization,
            role_codenames=None,
            extra_fields={k: data[k] for k in MemberService.MEMBERSHIP_FIELDS if data.get(k)},
        )

        if data.get('is_professional'):
            ProfessionalService.create_for_member(membership, data)

        OnboardingService.send_member_activation(membership, request=request)

        logger.info(
            "Membro criado: user=%s org=%s professional=%s",
            user.email, organization.slug, bool(data.get('is_professional')),
        )
        return membership
