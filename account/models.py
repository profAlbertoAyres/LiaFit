import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone

from core.enums.account import Gender
from core.managers import UserManager
from core.models.base import BaseModel
from core.models.tenant import TenantModel
from core.utils.uploads import smart_upload_to


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    fullname = models.CharField(max_length=150, verbose_name='Nome')
    email = models.EmailField('Email', unique=True)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    photo = models.ImageField(
        'Foto',
        upload_to=smart_upload_to,
        blank=True,
        null=True,
    )
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

    def get_full_name(self):
        return self.fullname

    def get_short_name(self):
        return self.fullname.split(' ')[0] if self.fullname else self.email

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def is_shadow(self) -> bool:
        return (
                self.is_active
                and self.email_verified_at is None
                and not self.has_usable_password()
        )


class Organization(BaseModel):
    company_name = models.CharField(verbose_name='Nome', max_length=255)
    slug = models.SlugField(verbose_name='Slug', unique=True)
    document = models.CharField(verbose_name='CNPJ/CPF', max_length=20, blank=True)
    phone = models.CharField(verbose_name='Telefone', max_length=20, blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)
    is_active = models.BooleanField(verbose_name='Ativa', default=False)

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
        return self.company_name


class OrganizationMember(BaseModel):
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


class ActiveClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)


class Professional(TenantModel, BaseModel):
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


class Client(BaseModel):
    user = models.OneToOneField(
        'account.User',
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Usuário',
    )

    class Meta:
        verbose_name = 'Perfil de Cliente'
        verbose_name_plural = 'Perfis de Clientes'

    def __str__(self):
        return f"Cliente: {self.user.fullname or self.user.email}"


class OrganizationClient(BaseModel):
    user = models.ForeignKey(
        'account.Client',
        on_delete=models.PROTECT,
        related_name='client_links',
        verbose_name='Usuário',
    )
    organization = models.ForeignKey(
        'account.Organization',
        on_delete=models.CASCADE,
        related_name='client_links',
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
    objective = models.TextField(
        'Objetivo',
        blank=True,
        help_text='Ex: emagrecimento, hipertrofia, condicionamento, '
                  'reabilitação, qualidade de vida.',
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
                condition=Q(archived_at__isnull=True),
                name='unique_active_client_org',
            )
        ]

    def __str__(self):
        return f"{self.user} ← cliente de → {self.organization}"

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None


class Assistant(TenantModel, BaseModel):
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


# 🔑 ONBOARDING TOKEN
class OnboardingToken(BaseModel):
    class Purpose(models.TextChoices):
        ONBOARDING = 'onboarding', 'Onboarding'
        RESET_PASSWORD = 'reset_password', 'Reset de Senha'
        EMAIL_CHANGE = 'email_change', 'Troca de Email'
        EMAIL_VERIFICATION = 'email_verification', 'Verificação de Email'
        INVITATION = 'invitation', 'Convite para Organização'
        MAGIC_LINK = 'magic_link', 'Login via Magic Link'

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='onboarding_tokens',
                             verbose_name='Usuário', )
    organization = models.ForeignKey('account.Organization', on_delete=models.CASCADE, related_name='onboarding_tokens',
                                     null=True, blank=True, verbose_name='Organização',
                                     help_text='Preenchido apenas em fluxos vinculados a uma organização (ex: onboarding).', )
    token = models.UUIDField('Token', default=uuid.uuid4, unique=True, editable=False, )
    purpose = models.CharField('Finalidade', max_length=32, choices=Purpose.choices, )
    expires_at = models.DateTimeField('Expira em')
    created_ip = models.GenericIPAddressField('IP de criação', null=True, blank=True,
                                              help_text='IP de quem solicitou a criação do token.', )
    created_ua = models.CharField('User Agent (criação)', max_length=255, null=True, blank=True, )
    used_at = models.DateTimeField('Utilizado em', null=True, blank=True)
    used_ip = models.GenericIPAddressField('IP de uso', null=True, blank=True)
    used_ua = models.CharField('User Agent', max_length=255, null=True, blank=True)
    data = models.JSONField('Dados extras', null=True, blank=True)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'
        indexes = [
            models.Index(fields=['user', 'purpose', 'used_at']),
        ]

    def __str__(self):
        return str(self.token)

    def __repr__(self):
        return f"<OnboardingToken {self.token} ({self.purpose})>"

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired
