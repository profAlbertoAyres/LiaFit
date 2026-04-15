from django.db import models


class TenantModel(models.Model):

    organization = models.ForeignKey(
        "account.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        db_index=True
    )

    objects = TenantManager()

    class Meta:
        abstract = True

    @classmethod
    def for_tenant(cls, organization):
        return cls.objects.filter(organization=organization)