from django.db import models


class ModuleChoices(models.TextChoices):
    SCHEDULING = 'scheduling', 'Scheduling'
    FINANCIAL = 'financial', 'Financial'
    WORKOUT = 'workout', 'Workout'
    NUTRITION = 'nutrition', 'Nutrition'
    MANAGEMENT = 'management', 'Management'