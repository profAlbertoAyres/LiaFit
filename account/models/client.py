from django.db import models
from django.db.models import Q
from core.models.base import BaseModel


class ActiveClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)


class Client(BaseModel):
    user = models.OneToOneField('account.User', on_delete=models.CASCADE, related_name='client_profile',
                                verbose_name='Usuário')

    class Meta:
        verbose_name = 'Perfil de Cliente'
        verbose_name_plural = 'Perfis de Clientes'

    def __str__(self):
        return f"Cliente: {self.user.fullname or self.user.email}"


class OrganizationClient(BaseModel):
    user = models.ForeignKey('account.Client', on_delete=models.PROTECT, related_name='client_links',
                             verbose_name='Usuário')
    organization = models.ForeignKey('account.Organization', on_delete=models.CASCADE, related_name='client_links',
                                     verbose_name='Organização')

    created_by = models.ForeignKey(
        'account.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_client_links', verbose_name='Cadastrado por'
    )

    first_service_at = models.DateTimeField('Primeiro serviço em', null=True, blank=True)
    welcome_email_sent = models.BooleanField('Email de boas-vindas enviado', default=False)
    objective = models.TextField('Objetivo', blank=True)
    notes = models.TextField('Observações internas da empresa', blank=True)
    archived_at = models.DateTimeField('Arquivado em', null=True, blank=True)

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
