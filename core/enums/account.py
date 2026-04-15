from django.db import models


class Gender(models.TextChoices):
    FEMALE = 'F', 'Feminino'
    MALE = 'M', 'Masculino'
    OTHER = 'O', 'Outro'