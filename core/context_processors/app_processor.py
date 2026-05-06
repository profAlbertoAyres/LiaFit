# core/context_processors/app_processor.py
"""
Context processor de configurações globais da aplicação.

Injeta variáveis de branding (nome, domínio, e-mail de suporte) em todos
os templates. Não depende de autenticação nem de tenant.
"""
from django.conf import settings


def app_settings(request):
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'Lia Linda'),
        'APP_DOMAIN': getattr(settings, 'APP_DOMAIN', 'lialinda.com.br'),
        'APP_SUPPORT_EMAIL': getattr(
            settings, 'APP_SUPPORT_EMAIL', 'suporte@lialinda.com.br'
        ),
    }
