from django.db import models


class Module(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    is_core = models.BooleanField(default=False)

    def __str__(self):
        return self.name
