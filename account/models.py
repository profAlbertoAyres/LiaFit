import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.enums.account import Gender
from core.management import UserManager
from core.models.base import BaseModel
from core.models.tenant import TenantModel
from core.utils.uploads import smart_upload_to


# ─────────────────────────────────────────────
# 👤 USER
# ─────────────────────────────────────────────

class User(AbstractUser):

    username = None

    # Identificação
    email = models.EmailField('Email', unique=True)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    photo = models.ImageField(
        'Foto',
        upload_to=smart_upload_to,
        blank=True,
        null=True,
    )

    # Dados pessoais globais
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    gender = models.CharField(
        'Gênero',
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )
    emergency_contact = models.CharField(
        'Contato de Emergência', max_length=100, blank=True,
    )
    emergency_phone = models.CharField(
        'Telefone de Emergência', max_length=20, blank=True,
    )

    # Validação de email (NÃO bloqueia login — é informativo)
    email_verified_at = models.DateTimeField(
        'Email verificado em', null=True, blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def is_shadow(self) -> bool:
        """Cliente cadastrado pela empresa que nunca acessou o sistema."""
        return (
            self.is_active
            and self.email_verified_at is None
            and not self.has_usable_password()
        )


# ─────────────────────────────────────────────
# 🏢 ORGANIZATION (TENANT)
# ─────────────────────────────────────────────

class Organization(BaseModel):

    name = models.CharField('Nome', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    document = models.CharField('CNPJ/CPF', max_length=20, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    is_active = models.BooleanField('Ativa', default=False)

    owner = models.ForeignKey(
        'account.User',
        on_delete=models.PROTECT,
        related_name='owned_organizations',
        verbose_name='Proprietário',
        null=True,
        blank=True,
        help_text='Sempre preenchido via OnboardingService.register(). '
                  'Nullable apenas por ordem de criação na transaction.',
    )

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# 🔗 ORGANIZATION MEMBER (VÍNCULO STAFF)
# ─────────────────────────────────────────────

class OrganizationMember(BaseModel):
    """
    Vínculo de STAFF entre User e Organization.

    Um usuário pode pertencer a várias organizações.
    Os papéis (roles) são M2M — um membro pode ser
    PROFESSIONAL e ADMIN ao mesmo tempo.

    Regra: NUNCA atribuir role CLIENT aqui. Ser cliente
    materializa-se em OrganizationClient (vínculo separado).
    """
    user = models.ForeignKey(
        'account.User',
        on_delete=models.PROTECT,
        related_name='memberships',
        verbose_name='Usuário',
    )
    organization = models.ForeignKey(
        'account.Organization',
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Organização',
    )
    roles = models.ManyToManyField(
        'core.Role',
        related_name='members',
        verbose_name='Papéis',
        blank=True,
    )
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Membro da Organização'
        verbose_name_plural = 'Membros da Organização'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization'],
                name='unique_member_org',
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.organization}"


# ─────────────────────────────────────────────
# 🧑‍🤝‍🧑 ORGANIZATION CLIENT (VÍNCULO CLIENTE)
# ─────────────────────────────────────────────

class ActiveClientManager(models.Manager):
    """Manager padrão: retorna apenas vínculos não arquivados."""
    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)


class OrganizationClient(BaseModel):
    """
    Vínculo entre User (cliente global) e Organization.

    Regra de negócio:
    - Nasce quando o cliente agenda o 1º serviço OU quando a empresa
      cadastra proativamente (shadow client).
    - Antes desse vínculo existir, a empresa NÃO enxerga o user.
    - Um mesmo user pode ter vínculos com várias organizações.
    - Desvínculo NUNCA deleta — preenche archived_at (preserva histórico).

    Managers:
      - objects       → apenas vínculos ativos (archived_at IS NULL)
      - all_objects   → todos, inclusive arquivados (auditoria, histórico)
    """
    user = models.ForeignKey(
        'account.User',
        on_delete=models.PROTECT,
        related_name='client_links',
        verbose_name='Usuário',
    )
    organization = models.ForeignKey(
        'account.Organization',
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Organização',
    )
    created_by = models.ForeignKey(
        'account.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_client_links',
        verbose_name='Cadastrado por',
        help_text='Membro da empresa que criou o vínculo (shadow client). '
                  'Vazio se o cliente se cadastrou sozinho.',
    )
    first_service_at = models.DateTimeField(
        'Primeiro serviço em',
        null=True, blank=True,
        help_text='Preenchido automaticamente no 1º agendamento.',
    )
    welcome_email_sent = models.BooleanField(
        'Email de boas-vindas enviado',
        default=False,
    )
    notes = models.TextField('Observações internas da empresa', blank=True)
    archived_at = models.DateTimeField(
        'Arquivado em',
        null=True, blank=True,
        help_text='Preenchido ao desvincular cliente. '
                  'Preserva histórico operacional — use ClientService.archive().',
    )

    objects = ActiveClientManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Cliente da Organização'
        verbose_name_plural = 'Clientes da Organização'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization'],
                name='unique_client_org',
            )
        ]

    def __str__(self):
        return f"{self.user} ← cliente de → {self.organization}"

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None


# ─────────────────────────────────────────────
# 🏋️ PROFESSIONAL (PERFIL)
# ─────────────────────────────────────────────

class Professional(TenantModel, BaseModel):
    """
    Perfil do profissional (personal trainer, fisioterapeuta, nutricionista, etc.).
    Extensão 1:1 de um OrganizationMember.

    Contém APENAS dados específicos da atuação profissional na organização.
    Dados pessoais (nome, foto, telefone) ficam no User.
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='professional_profile',
        verbose_name='Membro',
    )
    specialty = models.CharField('Especialidade', max_length=100, blank=True)
    registration_type = models.CharField(
        'Tipo de Registro',
        max_length=10,
        blank=True,
        help_text='Ex: CREF, CRP, CRN, CREFITO',
    )
    registration_number = models.CharField(
        'Nº Registro',
        max_length=50,
        blank=True,
    )
    bio = models.TextField('Bio', blank=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'

    def __str__(self):
        user = self.member.user
        return f"Prof. {user.get_full_name() or user.email}"


# ─────────────────────────────────────────────
# 🧑 CLIENT (PERFIL)
# ─────────────────────────────────────────────

class Client(TenantModel, BaseModel):
    """
    Perfil do cliente dentro de uma organização específica.
    Extensão 1:1 de um OrganizationClient.

    Contém APENAS dados do cliente relevantes para a empresa atual
    (objetivo, metas, preferências de treino etc.).
    Dados pessoais (nome, data de nascimento, contato de emergência)
    ficam no User — são globais.

    Por que 1:1 com OrganizationClient e não com User?
    → O objetivo muda de contexto: na academia pode ser "hipertrofia",
      na clínica pode ser "reabilitação". Mesma pessoa, objetivos distintos.
    """
    organization_client = models.OneToOneField(
        'account.OrganizationClient',
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Vínculo com a Organização',
    )
    objective = models.TextField(
        'Objetivo',
        blank=True,
        help_text='Ex: emagrecimento, hipertrofia, condicionamento, '
                  'reabilitação, qualidade de vida.',
    )

    class Meta:
        verbose_name = 'Perfil de Cliente'
        verbose_name_plural = 'Perfis de Clientes'

    def __str__(self):
        user = self.organization_client.user
        return f"Cliente: {user.get_full_name() or user.email}"


# ─────────────────────────────────────────────
# 📋 ASSISTANT (PERFIL)
# ─────────────────────────────────────────────

class Assistant(TenantModel, BaseModel):
    """
    Perfil do recepcionista/assistente.
    Extensão 1:1 de um OrganizationMember.
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='assistant_profile',
        verbose_name='Membro',
    )
    department = models.CharField('Setor', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Assistente'
        verbose_name_plural = 'Assistentes'

    def __str__(self):
        user = self.member.user
        return f"Assistente: {user.get_full_name() or user.email}"


# ─────────────────────────────────────────────
# 🔑 ONBOARDING TOKEN
# ─────────────────────────────────────────────

class OnboardingToken(BaseModel):
    """
    Token de uso único para ações de onboarding:
      - Setup de senha do owner (registro de empresa)
      - Validação de email do auto-registro (pós-Sprint 3)

    Nota futura (N5): avaliar unificação com tokens de reset de senha
    e troca de email num único UserToken com campo purpose.
    """
    user = models.ForeignKey(
        'account.User',
        on_delete=models.CASCADE,
        related_name='onboarding_tokens',
        verbose_name='Usuário',
    )
    token = models.UUIDField(
        'Token', default=uuid.uuid4, unique=True, editable=False,
    )
    expires_at = models.DateTimeField('Expira em')
    used_at = models.DateTimeField(
        'Utilizado em', null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Token de Onboarding'
        verbose_name_plural = 'Tokens de Onboarding'

    def __str__(self):
        return str(self.token)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired
