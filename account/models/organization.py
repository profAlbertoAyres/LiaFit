from django.db import models
from core.models.base import BaseModel
from core.utils.uploads import smart_upload_to


class Organization(BaseModel):
    company_name = models.CharField(verbose_name='Nome', max_length=255)
    slug = models.SlugField(verbose_name='Slug', unique=True)
    document = models.CharField(verbose_name='CNPJ/CPF', max_length=20, blank=True)
    phone = models.CharField(verbose_name='Telefone', max_length=20, blank=True)
    email = models.EmailField(verbose_name='Email', blank=True)

    logo = models.ImageField('Logo', upload_to=smart_upload_to, blank=True, null=True)
    city = models.CharField('Cidade', max_length=100, blank=True)
    state = models.CharField('Estado (UF)', max_length=2, blank=True)

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
