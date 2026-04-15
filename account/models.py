import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from core.enums.account import Gender
from core.models.base import BaseModel, TenantMixin
from core.models.role import Role
from core.models.tenant import TenantModel
from core.utils.uploads import smart_upload_to

User = get_user_model()


# Create your models here.
class Organization(BaseModel):
    company_name = models.CharField(max_length=150, verbose_name='Razão Social')
    name = models.CharField(max_length=255, verbose_name='Nome Fantásia', blank=True, null=True)
    slug = models.SlugField(unique=True)

    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)

    owner_email = models.EmailField()
    phone = models.CharField(max_length=20)

    zip_code = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    address_number = models.CharField(max_length=20)
    complement = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    logo = models.ImageField(upload_to=smart_upload_to, blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_organizations'
    )

    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pendente'), ('active', 'Ativo')],
        default='pending'
    )

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name or self.company_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.company_name


class UserOrganization(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    must_change_password = models.BooleanField(default=True)
    photo = models.ImageField(upload_to=smart_upload_to, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user}"



class Professional(TenantModel, BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='professionals')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='professionals')

    cref = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user} ({self.organization})"


class Client(TenantModel, BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='clients')

    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    goal = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=[
        ('lead', 'Interessado'),
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
    ], default='lead')

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'organization')


class Assistant(TenantModel, BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistants')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='assistants')


class ClientProfessional(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('client', 'professional')

    def __str__(self):
        return f"{self.client} → {self.professional}"


class AssistantProfessional(BaseModel):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('assistant', 'professional')

    def __str__(self):
        return f"{self.assistant} → {self.professional}"


# SUPPLIER

class Supplier(TenantMixin, BaseModel):
    SUPPLIER_TYPE = [
        ('global', 'Global'),
        ('custom', 'Customizado'),
    ]

    name = models.CharField(max_length=150)
    document = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    owner = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='suppliers'
    )

    supplier_type = models.CharField(max_length=10, choices=SUPPLIER_TYPE, default='custom')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


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