from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em', editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em', editable=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} #{self.pk}"
