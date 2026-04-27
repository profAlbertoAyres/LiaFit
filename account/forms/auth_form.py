from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

from core.forms.base_form import LiaFitStyleMixin


class LoginForm(LiaFitStyleMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'username' in self.fields:
            self.fields['username'].widget.input_type = 'email'
            self.fields['username'].label = _('E-mail')
            self.fields['username'].widget.attrs['autocomplete'] = 'email'

        if 'password' in self.fields:
            self.fields['password'].label = _("Senha")

        self._apply_liafit_styles()
