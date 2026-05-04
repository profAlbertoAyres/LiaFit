from django.db import models
from core.models.base import BaseModel
from core.utils.uploads import smart_upload_to
from core.constants.locations import BRAZILIAN_STATES


class Organization(BaseModel):
    company_name = models.CharField(verbose_name='Nome', max_length=255)
    slug = models.SlugField(verbose_name='Slug', unique=True)
    document = models.CharField(verbose_name='CNPJ/CPF', unique=True, max_length=20, blank=True, null=True)
    phone = models.CharField(verbose_name='Telefone', max_length=20, blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)

    logo = models.ImageField('Logo', upload_to=smart_upload_to, blank=True, null=True)
    zip_code = models.CharField("CEP", max_length=9, blank=True)  # 12345-678
    address = models.CharField("Endereço", max_length=255, blank=True)
    number = models.CharField('Número', max_length=20, blank=True, null=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('Estado (UF)', max_length=2, blank=True, choices=BRAZILIAN_STATES,)

    is_active = models.BooleanField(verbose_name='Ativa', default=False)

    owner = models.ForeignKey(
        'account.User', on_delete=models.PROTECT, related_name='owned_organizations',
        verbose_name='Proprietário', null=True, blank=True
    )

    class Meta:
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self):
        return self.company_name
