from django.db import models
from django.utils import timezone

from core.models.base import BaseModel
from django.utils.translation import gettext_lazy as _

class RemunerationType(models.TextChoices):
    FIXED = 'fixed', _('Salário Fixo')
    COMMISSION = 'commission', _('Apenas Comissão')
    BOTH = 'both', _('Fixo + Comissão')

class OrganizationMember(BaseModel):
    user = models.ForeignKey('account.User', on_delete=models.PROTECT, related_name='memberships', verbose_name='Usuário')
    organization = models.ForeignKey('account.Organization', on_delete=models.CASCADE, related_name='members', verbose_name='Organização')
    roles = models.ManyToManyField('core.Role', related_name='members', verbose_name='Papéis', blank=True)
    is_active = models.BooleanField('Ativo', default=True)
    remuneration_type = models.CharField(max_length=20, choices=RemunerationType.choices, default=RemunerationType.FIXED, verbose_name=_('Tipo de Remuneração'))

    joined_at = models.DateField(default=timezone.now, verbose_name=_('Data de Admissão'))
    left_at = models.DateField(null=True, blank=True, verbose_name=_('Data de Desligamento'))

    class Meta:
        verbose_name = 'Membro da Organização'
        verbose_name_plural = 'Membros da Organização'
        constraints = [
            models.UniqueConstraint(fields=['user', 'organization'], name='unique_member_org')
        ]

    def __str__(self):
        return f"{self.user} → {self.organization}"

    @property
    def highest_role(self):
        return self.roles.filter(is_active=True).order_by('-level').first()

    @property
    def highest_role_name(self) -> str | None:
        role = self.highest_role
        return role.name if role else None

    @property
    def highest_role_level(self) -> int | None:
        role = self.highest_role
        return role.level if role else None
