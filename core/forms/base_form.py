from django import forms
from django.db.models import QuerySet


class LiaLindaStyleMixin:
    # Mapa de ícones default por tipo de input
    # Pode ser sobrescrito via widget.attrs['lia_icon'] = 'outro-icone'
    # Ou desligado via widget.attrs['lia_icon'] = 'none'
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
            )):
                css_class = 'lia-form-control'

            elif isinstance(field.widget, forms.Select):
                css_class = 'lia-form-control'

            elif isinstance(field.widget, (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple,
            )):
                css_class = 'form-check-input'

            elif isinstance(field.widget, forms.ClearableFileInput):
                css_class = 'lia-form-control'

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

            # Aplica ícone default se o dev não definiu manualmente
            self._apply_default_icon(field)

    def _apply_default_icon(self, field):
        if 'lia_icon' in field.widget.attrs:
            return

        input_type = getattr(field.widget, 'input_type', None)
        default_icon = self.ICON_DEFAULTS.get(input_type, '') if input_type else ''
        field.widget.attrs['lia_icon'] = default_icon


class TenantKwargsMixin:
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        self.membership = kwargs.pop('membership', None)
        self.professional = kwargs.pop('professional', None)
        super().__init__(*args, **kwargs)


class BaseForm(TenantKwargsMixin, LiaLindaStyleMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_lialinda_styles()


class BaseModelForm(TenantKwargsMixin, LiaLindaStyleMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_tenant_filter()
        self._apply_lialinda_styles()

    def _apply_tenant_filter(self):
        if not self.tenant:
            return

        is_superuser = False

        for field in self.fields.values():
            if not (hasattr(field, 'queryset') and isinstance(field.queryset, QuerySet)):
                continue

            model = field.queryset.model
            qs = field.queryset

            if any(f.name == 'organization' for f in model._meta.fields):
                qs = qs.filter(organization=self.tenant)

            if (
                self.membership
                and not is_superuser
                and any(f.name == 'member' for f in model._meta.fields)
            ):
                qs = qs.filter(member=self.membership)

            field.queryset = qs
