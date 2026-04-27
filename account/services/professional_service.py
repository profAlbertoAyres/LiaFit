# account/services/professional_service.py
import logging
from django.db import transaction
from account.models import Professional

logger = logging.getLogger(__name__)


class ProfessionalService:

    @staticmethod
    @transaction.atomic
    def create_for_member(membership, data: dict) -> Professional:

        professional = Professional.objects.create(
            organization=membership.organization,  # TenantModel exige
            member=membership,
            registration_type=data.get('registration_type', ''),
            registration_number=data.get('registration_number', ''),
            bio=data.get('bio', ''),
        )

        specialties = data.get('specialties')
        if specialties:
            professional.specialties.set(specialties)

        logger.info(
            "Professional criado: member=%s reg=%s/%s",
            membership.user.email,
            data.get('registration_type'),
            data.get('registration_number'),
        )
        return professional
