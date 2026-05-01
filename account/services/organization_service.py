import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from account.models import Organization, OrganizationMember
from core.models.role import Role
from core.services.bootstrap import bootstrap_organization

logger = logging.getLogger(__name__)


class OrganizationService:

    # ──────────────── CRIAÇÃO ────────────────

    @staticmethod
    @transaction.atomic
    def create_organization(data, owner=None):
        """
        Cria a organização (inativa) + executa bootstrap (roles, permissões, módulos).
        Se `owner` for informado, vincula como dono e membro com role 'owner'.
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

        # 🔧 Bootstrap: cria roles + permissões + módulos
        stats = bootstrap_organization(organization)
        logger.info(
            "Bootstrap: modules=%d roles_created=%d roles_updated=%d perms=%d",
            stats["modules_enabled"],
            stats["roles_created"],
            stats["roles_updated"],
            stats["role_permissions_created"],
        )

        # 🔗 Owner vira membro automaticamente
        if owner:
            OrganizationService.add_member(owner, organization, role_codenames="owner")

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
    def add_member(user, organization, role_codenames=None, extra_fields: dict | None = None):
        # Normaliza para lista de slugs em lowercase
        if isinstance(role_codenames, str):
            slugs = [role_codenames.lower()]
        else:
            slugs = [code.lower() for code in (role_codenames or []) if code]

        roles = []
        if slugs:
            roles_qs = Role.objects.filter(slug__in=slugs, organization=organization)
            found_slugs = set(roles_qs.values_list("slug", flat=True))
            missing = set(slugs) - found_slugs
            if missing:
                raise ValidationError(f"Roles não encontrados: {', '.join(sorted(missing))}")
            roles = list(roles_qs)

        membership, created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=organization,
            defaults=extra_fields or {},
        )

        if roles:
            membership.roles.add(*roles)

        logger.info(
            "Membership %s: user=%s org=%s roles=%s",
            "criado" if created else "atualizado",
            user.email, organization.slug, slugs or "—",
        )
        return membership

    # ──────────────── ATIVAÇÃO ────────────────

    @staticmethod
    @transaction.atomic
    def activate_organization(organization):
        """Idempotente: marca a organização como ativa, se ainda não estiver."""
        if organization.is_active:
            logger.debug("Organização %s já estava ativa.", organization.slug)
            return organization

        organization.is_active = True
        organization.save(update_fields=["is_active"])
        logger.info("Organização ativada: %s", organization.slug)
        return organization
