from django.db import models


class AssistantPermission(models.TextChoices):
    VIEW_DASHBOARD = 'VIEW_DASHBOARD', 'Ver Dashboard'
    MANAGE_CLIENTS = 'MANAGE_CLIENTS', 'Gerenciar Clientes'
    VIEW_FINANCIAL = 'VIEW_FINANCIAL', 'Ver Financeiro'
    MANAGE_SCHEDULE = 'MANAGE_SCHEDULE', 'Gerenciar Agenda'
    MANAGE_WORKOUTS = 'MANAGE_WORKOUTS', 'Gerenciar Treinos'