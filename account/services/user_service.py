from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:

    @staticmethod
    def get_or_create_user(email, user_data):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "is_active": False,
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        return user

    @staticmethod
    def setup_profile(user, user_data):
        from account.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=user)

        profile.phone = user_data.get("phone")
        profile.photo = user_data.get("photo")
        profile.must_change_password = True
        profile.save()

        return profile