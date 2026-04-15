from django.db import models
from core.models.base import BaseModel


class Role(BaseModel):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name