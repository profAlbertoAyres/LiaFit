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
    """
    Usuário customizado — login por email.
    Não possui username. O email é o identificador único.
    """
    username = None
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    is_verified = models.BooleanField('Email verificado', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email


# ─────────────────────────────────────────────
# 🏢 ORGANIZATION (TENANT)
# ─────────────────────────────────────────────

class Organization(BaseModel):
    """
    Academia, estúdio, clínica — o tenant do sistema.
    Cada organização é um espaço isolado de dados.
    """
    name = models.CharField('Nome', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    document = models.CharField('CNPJ/CPF', max_length=20, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    is_active = models.BooleanField('Ativa', default=True)

    owner = models.ForeignKey(
        'account.User',
        on_delete=models.PROTECT,
        related_name='owned_organizations',
        verbose_name='Proprietário',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# 🔗 ORGANIZATION MEMBER (VÍNCULO USER ↔ ORG)
# ─────────────────────────────────────────────

class OrganizationMember(BaseModel):
    """
    Vínculo entre User e Organization.
    Um usuário pode pertencer a várias organizações.
    Os papéis (roles) são M2M — um membro pode ser
    PROFESSIONAL e ADMIN ao mesmo tempo.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Usuário',
    )
    organization = models.ForeignKey(
        Organization,
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
# 🏋️ PROFESSIONAL
# ─────────────────────────────────────────────

class Professional(TenantModel, BaseModel):
    """
    Perfil do profissional (personal trainer, fisioterapeuta, etc).
    Vinculado ao membro E à organização diretamente.
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
    registration_number = models.CharField('Nº Registro', max_length=50, blank=True)
    bio = models.TextField('Bio', blank=True)
    avatar = models.ImageField(
        'Foto',
        upload_to=smart_upload_to,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'

    def __str__(self):
        return f"Prof. {self.member.user.get_full_name() or self.member.user.email}"


# ─────────────────────────────────────────────
# 🧑‍🤝‍🧑 CLIENT
# ─────────────────────────────────────────────

class Client(TenantModel, BaseModel):
    """
    Perfil do cliente/aluno.
    Vinculado ao membro E à organização diretamente.
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Membro',
    )
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    gender = models.CharField(
        'Gênero',
        max_length=1,
        choices=Gender.choices,
        blank=True,
    )
    emergency_contact = models.CharField('Contato de Emergência', max_length=100, blank=True)
    emergency_phone = models.CharField('Telefone de Emergência', max_length=20, blank=True)
    notes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"Cliente: {self.member.user.get_full_name() or self.member.user.email}"


# ─────────────────────────────────────────────
# 📋 ASSISTANT
# ─────────────────────────────────────────────

class Assistant(TenantModel, BaseModel):
    """
    Perfil do recepcionista/assistente.
    Vinculado ao membro E à organização diretamente.
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
        return f"Assistente: {self.member.user.get_full_name() or self.member.user.email}"


class PasswordSetupToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return str(self.token)

    def is_valid(self):
        return not self.used and not self.is_expired()

    def is_expired(self):
        return timezone.now() > self.expires_at