from django.db import models
from core.models.base import BaseModel
from core.models.tenant import TenantModel

class RegistrationType(models.TextChoices):
    CREF  = 'CREF',  'CREF (Educação Física)'
    CRP   = 'CRP',   'CRP (Psicologia)'
    CRN   = 'CRN',   'CRN (Nutrição)'
    CREFITO = 'CREFITO', 'CREFITO (Fisioterapia)'
    CRM   = 'CRM',   'CRM (Medicina)'
    OTHER = 'OTHER', 'Outro'

class Professional(TenantModel, BaseModel):
    member = models.OneToOneField('account.OrganizationMember', on_delete=models.CASCADE,
                                  related_name='professional_profile', verbose_name='Membro')

    specialties = models.ManyToManyField('account.Specialty', related_name='professionals',
                                         verbose_name='Especialidades', blank=True)
    registration_type = models.CharField(max_length=20, choices=RegistrationType.choices, null=True, blank=True)
    registration_number = models.CharField('Nº Registro', max_length=50, blank=True)
    bio = models.TextField('Bio', blank=True)

    class Meta:
        verbose_name = 'Profissional'
        verbose_name_plural = 'Profissionais'

    def __str__(self):
        user = self.member.user
        return f"Prof. {user.get_full_name() or user.email}"


class Assistant(TenantModel, BaseModel):
    member = models.OneToOneField('account.OrganizationMember', on_delete=models.CASCADE,
                                  related_name='assistant_profile', verbose_name='Membro')
    department = models.CharField('Setor', max_length=100, blank=True)

    # 🆕 Conforme sua regra: o assistente responde a um profissional específico
    linked_professional = models.ForeignKey(
        'account.Professional', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assistants', verbose_name='Profissional Vinculado',
        help_text='Profissional ao qual este assistente está subordinado/atende.'
    )

    class Meta:
        verbose_name = 'Assistente'
        verbose_name_plural = 'Assistentes'

    def __str__(self):
        user = self.member.user
        return f"Assistente: {user.get_full_name() or user.email}"
