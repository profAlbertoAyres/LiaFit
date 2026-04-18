from account.services.token_service import TokenService


class ActivationService:
    @staticmethod
    def setup_password(token, password):
        token_obj = TokenService.get_valid_token(token)
        if not token_obj:
            raise Exception("Token inválido.")

        user = token_obj.user
        user.set_password(password)
        user.is_active = True
        user.save()
        token_obj.is_valid = False
        token_obj.save()
        return user
