from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Registra os menus estáticos sempre que o servidor rodar
        try:
            # Ajuste o import caso a pasta 'config' esteja em outro lugar
            from core.config.menus import register_menus
            register_menus()
        except ImportError:
            pass