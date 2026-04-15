from django.db import models


class Module(models.Model):

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50,unique=True)

    is_core = models.BooleanField(default=False)

    def __str__(self):
        return self.name