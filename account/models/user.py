import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.enums.account import Gender
from core.managers import UserManager
from core.models import BaseModel
from core.utils.uploads import smart_upload_to


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    fullname = models.CharField(max_length=150, verbose_name='Nome')
    email = models.EmailField('Email', unique=True)
    cpf = models.CharField('CPF', max_length=14, blank=True)
    phone = models.CharField('Telefone', max_length=20, blank=True)
    photo = models.ImageField('Foto', upload_to=smart_upload_to, blank=True, null=True)
    birth_date = models.DateField('Data de Nascimento', null=True, blank=True)
    gender = models.CharField('Gênero', max_length=1, choices=Gender.choices, blank=True)

    email_verified_at = models.DateTimeField('Email verificado em', null=True, blank=True)

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

    def get_permission_codenames(self, organization) -> set[str]:
        if self.is_superuser:
            from core.models import Permission
            return set(Permission.objects.values_list('codename', flat=True))

        if not organization:
            return set()

        from core.models import RolePermission
        return set(
            RolePermission.objects
            .filter(
                organization=organization,
                role__members__user=self,
                role__members__organization=organization,
                role__members__is_active=True,
                role__is_active=True,
            )
            .values_list('permission__codename', flat=True)
            .distinct()
        )

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


class OnboardingToken(BaseModel):
    class Purpose(models.TextChoices):
        ONBOARDING = 'onboarding', 'Onboarding'
        RESET_PASSWORD = 'reset_password', 'Reset de Senha'
        EMAIL_CHANGE = 'email_change', 'Troca de Email'
        EMAIL_VERIFICATION = 'email_verification', 'Verificação de Email'
        INVITATION = 'invitation', 'Convite para Organização'
        MAGIC_LINK = 'magic_link', 'Login via Magic Link'
        ORG_ACTIVATION = 'org_activation', 'Ativação de Empresa Adicional'
        

    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='onboarding_tokens',
                             verbose_name='Usuário')
    organization = models.ForeignKey('account.Organization', on_delete=models.CASCADE, related_name='onboarding_tokens',
                                     null=True, blank=True)
    token = models.UUIDField('Token', default=uuid.uuid4, unique=True, editable=False)
    purpose = models.CharField('Finalidade', max_length=32, choices=Purpose.choices)
    expires_at = models.DateTimeField('Expira em')

    created_ip = models.GenericIPAddressField('IP de criação', null=True, blank=True)
    created_ua = models.CharField('User Agent (criação)', max_length=255, null=True, blank=True)
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

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired
