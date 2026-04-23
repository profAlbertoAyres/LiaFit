import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from account.models import Organization, OrganizationMember
from core.bootstrap import bootstrap_organization
from core.models.role import Role

logger = logging.getLogger(__name__)


class OrganizationService:

    # ──────────────── CRIAÇÃO ────────────────

    @staticmethod
    @transaction.atomic
    def create_organization(data, owner=None):
        """
        Cria a organização (inativa) + executa bootstrap (roles, permissões, módulos).
        Se `owner` for informado, já vincula como dono e membro com role 'owner'.
        """
        company_name = data.get("company_name")
        if not company_name:
            raise ValidationError("company_name é obrigatório.")

        slug = data.get("slug") or OrganizationService._generate_unique_slug(company_name)

        organization = Organization.objects.create(
            company_name=company_name,
            slug=slug,
            document=data.get("document", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            owner=owner,
        )

        logger.info(
            "Organização criada: id=%s name=%s slug=%s",
            organization.id, company_name, slug,
        )

        # 🔧 Bootstrap: cria roles + permissões + módulos logo na criação
        stats = bootstrap_organization(organization)
        logger.info(
            "Bootstrap: modules=%d roles_created=%d roles_updated=%d perms=%d",
            stats["modules_enabled"],
            stats["roles_created"],
            stats["roles_updated"],
            stats["role_permissions_created"],
        )

        # 🔗 Se houver owner, já adiciona como membro
        if owner:
            OrganizationService.add_member(owner, organization, role_codename="owner")

        return organization

    @staticmethod
    def _generate_unique_slug(company_name, max_attempts=100):
        base_slug = slugify(company_name)
        if not base_slug:
            raise ValidationError("Não foi possível gerar slug a partir do nome da empresa.")

        slug = base_slug
        counter = 2
        while Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            if counter > max_attempts:
                raise ValidationError(
                    f"Não foi possível gerar slug único após {max_attempts} tentativas."
                )
        return slug

    # ──────────────── MEMBROS ────────────────

    @staticmethod
    @transaction.atomic
    def add_member(user, organization, role_codename):
        try:
            role = Role.objects.get(
                slug=role_codename.lower(),
                organization=organization,
            )
        except Role.DoesNotExist:
            logger.error(
                "Role inexistente: org=%s codename=%s",
                organization.slug, role_codename,
            )
            raise ValidationError(f"Role '{role_codename}' não encontrada.")

        membership, created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=organization,
        )
        membership.roles.add(role)

        logger.info(
            "Membro %s: user=%s org=%s role=%s",
            "criado" if created else "atualizado",
            user.email, organization.slug, role_codename,
        )
        return membership

    # ──────────────── ATIVAÇÃO ────────────────

    @staticmethod
    @transaction.atomic
    def activate_organization(organization):
        """Apenas marca a organização como ativa (idempotente)."""
        if organization.is_active:
            logger.debug("Organização %s já estava ativa.", organization.slug)
            return organization

        organization.is_active = True
        organization.save(update_fields=["is_active"])
        logger.info("Organização ativada: %s", organization.slug)
        return organization
