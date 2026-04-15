from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import Organization, UserOrganization, Professional, Client, UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Cria ambiente SaaS de teste controlado"

    def handle(self, *args, **options):

        self.stdout.write("🔧 Criando ambiente de teste SaaS...")

        # =========================
        # 1. USERS
        # =========================
        admin_user, _ = User.objects.get_or_create(
            email="admin@fit.com",
            defaults={
                "first_name": "Admin",
                "last_name": "System",
                "username": "admin@fit.com",
                "is_active": True
            }
        )
        admin_user.set_password("123456")
        admin_user.save()

        client_user, _ = User.objects.get_or_create(
            email="client@fit.com",
            defaults={
                "first_name": "Client",
                "last_name": "Test",
                "username": "client@fit.com",
                "is_active": True
            }
        )
        client_user.set_password("123456")
        client_user.save()

        # =========================
        # 2. ORGANIZATION
        # =========================
        org, _ = Organization.objects.get_or_create(
            name="FitTest Academy",
            defaults={
                "company_name": "FitTest Academy LTDA",
                "owner_email": "admin@fit.com",
                "phone": "000000000",
                "zip_code": "00000-000",
                "address": "Rua Teste",
                "address_number": "123",
                "neighborhood": "Centro",
                "city": "Teste",
                "state": "RO",
                "owner": admin_user,
                "status": "active",
                "is_active": True
            }
        )

        # =========================
        # 3. MEMBERSHIPS
        # =========================
        UserOrganization.objects.get_or_create(
            user=admin_user,
            organization=org,
            role="admin"
        )

        UserOrganization.objects.get_or_create(
            user=client_user,
            organization=org,
            role="client"
        )

        # =========================
        # 4. PROFILE + CONTEXT TEST
        # =========================
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={"phone": "999999999"}
        )

        UserProfile.objects.get_or_create(
            user=client_user,
            defaults={"phone": "888888888"}
        )

        self.stdout.write(self.style.SUCCESS("✅ Ambiente SaaS criado com sucesso!"))