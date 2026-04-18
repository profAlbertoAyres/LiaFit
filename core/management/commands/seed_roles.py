# core/management/commands/seed_roles.py

from django.core.management.base import BaseCommand
from core.models import Role

ROLES_SEED = [
    {"codename": "OWNER", "name": "Proprietário", "level": 100},
    {"codename": "ADMIN", "name": "Administrador", "level": 80},
    {"codename": "PROFESSIONAL", "name": "Profissional", "level": 50},
    {"codename": "ASSISTANT", "name": "Assistente", "level": 30},
    {"codename": "CLIENT", "name": "Cliente", "level": 10},
]

class Command(BaseCommand):
    help = "Cria ou atualiza os papéis do sistema (Role seed)."

    def handle(self, *args, **options):
        for role_data in ROLES_SEED:
            obj, created = Role.objects.update_or_create(
                codename=role_data["codename"],
                defaults={
                    "name": role_data["name"],
                    "level": role_data["level"],
                },
            )
            action = "Criado" if created else "Atualizado"
            self.stdout.write(f"{action}: {obj.codename} ({obj.name})")

        self.stdout.write(self.style.SUCCESS("Seed de Roles concluído!"))
