from django.contrib.auth.models import AbstractUser
from django.db import models

from core.management import UserManager
from core.models.base import BaseModel


class User(AbstractUser):
    """
    Usuário customizado — login por email.
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


class Organization(BaseModel):
    """
    Academia, estúdio, clínica — o tenant do sistema.
    """
    name = models.CharField('Nome', max_length=255)
    slug = models.SlugField('Slug', unique=True)
    document = models.CharField('CNPJ/CPF', max_length=20, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    is_active = models.BooleanField('Ativa', default=True)

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.name


class OrganizationMember(BaseModel):
    """
    Vínculo entre User e Organization com um Role.
    Um usuário pode pertencer a várias organizações.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Usuário'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Organização'
    )
    role = models.ForeignKey(
        'core.Role',
        on_delete=models.PROTECT,
        related_name='members',
        verbose_name='Papel'
    )
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Membro da Organização'
        verbose_name_plural = 'Membros da Organização'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'organization', 'role'],
                name='unique_member_role'
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.organization} ({self.role})"


class Professional(BaseModel):
    """
    Dados específicos do profissional (personal trainer, fisioterapeuta, etc).
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='professional_profile',
        verbose_name='Membro'
    )
    specialty = models.CharField('Especialidade', max_length=100, blank=True)
    registration_number = models.CharField('CREF/Registro', max_length=50, blank=True)
    bio = models.TextField('Bio', blank=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'

    def __str__(self):
        return f"Prof. {self.member.user}"


class Client(BaseModel):
    """
    Dados específicos do cliente/aluno.
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='client_profile',
        verbose_name='Membro'
    )
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    gender = models.CharField(
        'Gênero',
        max_length=1,
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        blank=True
    )
    emergency_contact = models.CharField('Contato de Emergência', max_length=100, blank=True)
    emergency_phone = models.CharField('Telefone de Emergência', max_length=20, blank=True)
    notes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"Cliente: {self.member.user}"


class Assistant(BaseModel):
    """
    Dados específicos do recepcionista/assistente.
    """
    member = models.OneToOneField(
        OrganizationMember,
        on_delete=models.CASCADE,
        related_name='assistant_profile',
        verbose_name='Membro'
    )
    department = models.CharField('Setor', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Assistente'
        verbose_name_plural = 'Assistentes'

    def __str__(self):
        return f"Assistente: {self.member.user}"
