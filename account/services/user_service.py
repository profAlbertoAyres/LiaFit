from django.contrib.auth import get_user_model

from account.models import OrganizationMember

User = get_user_model()


class UserService:

    @staticmethod
    def get_or_create_user(email, fullname=None):
        defaults = {
            "email": email,
            "is_active": False,
        }

        if fullname:
            defaults["fullname"] = fullname

        user, created = User.objects.get_or_create(
            email=email,
            defaults=defaults,
        )

        if created:
                user.set_unusable_password()
                user.save()

        return user


    @staticmethod
    def activate_user(user, password):
        user.set_password(password)
        user.is_active = True
        user.save(update_fields=["password", "is_active"])

        profile = getattr(user, "profile", None)
        if profile:
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])

        return user
