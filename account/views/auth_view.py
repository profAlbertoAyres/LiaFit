

from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator

from django_ratelimit.decorators import ratelimit

from account.forms.auth_form import LoginForm


@method_decorator(
    ratelimit(key='post:username', rate='5/m', method='POST', block=True),
    name='post',
)
@method_decorator(
    ratelimit(key='ip', rate='20/m', method='POST', block=True),
    name='post',
)
class CustomLoginView(auth_views.LoginView):
    template_name = 'accounts/auth/login.html'
    form_class = LoginForm
