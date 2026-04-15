from django.db import models


class AppointmentStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Agendado'
    IN_PROGRESS = 'IN_PROGRESS', 'Em andamento'
    COMPLETED = 'COMPLETED', 'Concluído'
    CANCELED = 'CANCELED', 'Cancelado'
    NO_SHOW = 'NO_SHOW', 'Falta'
    BLOCKED = 'BLOCKED', 'Bloqueado'