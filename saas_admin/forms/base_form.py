from django import forms


class LiaLindaStyleMixin:
    # 🆕 Mapa de ícones default por tipo de input
    ICON_DEFAULTS = {
        'email': 'mail',
        'password': 'lock',
        'tel': 'phone',
        'url': 'link',
        'search': 'search',
        'date': 'calendar',
        'datetime-local': 'calendar',
        'time': 'clock',
        'number': 'hash',
    }

    def _apply_lialinda_styles(self):
        for field_name, field in self.fields.items():

            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True

            if isinstance(field.widget, (
                    forms.TextInput,
                    forms.NumberInput,
                    forms.EmailInput,
                    forms.DateInput,
                    forms.Textarea,
                    forms.URLInput,
                    forms.PasswordInput,
                    forms.Select,
                    forms.ClearableFileInput,
            )):
                css_class = 'lia-form-control'

            elif isinstance(field.widget, (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple,
            )):
                css_class = 'form-check-input'
            else:
                css_class = ''

            existing = field.widget.attrs.get('class', '')
            classes = set(existing.split())
            if css_class:
                classes.add(css_class)
            field.widget.attrs['class'] = ' '.join(classes)

            if (
                    not field.widget.attrs.get('placeholder') and
                    not isinstance(field.widget, (
                            forms.Select,
                            forms.ClearableFileInput,
                            forms.CheckboxInput,
                            forms.CheckboxSelectMultiple,
                    ))
            ):
                label_text = field.label or field_name.replace('_', ' ').capitalize()
                field.widget.attrs['placeholder'] = str(label_text).replace(':', '')

            if field.required:
                field.widget.attrs['required'] = True

            if field_name == 'email':
                field.widget.attrs['autocomplete'] = 'email'

            # 🆕 Aplica ícone default se o dev não definiu manualmente
            self._apply_default_icon(field)

    def _apply_default_icon(self, field):
        """
        Define data-icon no widget baseado no input_type, se ainda não foi definido.
        """
        if 'data-icon' in field.widget.attrs:
            return

        input_type = getattr(field.widget, 'input_type', None)
        if not input_type:
            return

        default_icon = self.ICON_DEFAULTS.get(input_type)
        if default_icon:
            field.widget.attrs['data-icon'] = default_icon


class SaaSBaseForm(LiaLindaStyleMixin, forms.Form):
    """Formulário base para o SaaS Admin."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_lialinda_styles()


class SaaSBaseModelForm(LiaLindaStyleMixin, forms.ModelForm):
    """ModelForm base para o SaaS Admin (Sem filtro de tenant nas foreign keys)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_lialinda_styles()
