from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    FEMALE = 'F', _('Feminino')
    MALE = 'M', _('Masculino')
    OTHER = 'O', _('Outro')
    NOT_INFORMED = 'N', _('Prefiro não informar')