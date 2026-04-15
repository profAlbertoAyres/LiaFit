from account.models import Organization, UserOrganization


class OrganizationService:

    @staticmethod
    def create_organization(data):
        return Organization.objects.create(
            company_name=data["company_name"],
            owner_email=data["owner_email"],
            phone=data["phone"],
            zip_code=data["zip_code"],
            address=data["address"],
            address_number=data["address_number"],
            complement=data.get("complement"),
            neighborhood=data["neighborhood"],
            city=data["city"],
            state=data["state"],
            status="pending"
        )

    @staticmethod
    def add_user(user, organization, role):
        return UserOrganization.objects.create(
            user=user,
            organization=organization,
            role=role
        )