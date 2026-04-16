from django.db import models


class TenantModel(models.Model):
    """
    Model abstrato para isolamento multi-tenant.
    Todo model que pertence a uma organização herda deste.
    """
    organization = models.ForeignKey(
        'account.Organization',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        db_index=True,
        verbose_name='Organização',
    )

    class Meta:
        abstract = True

    @classmethod
    def for_tenant(cls, organization):
        return cls.objects.filter(organization=organization)
