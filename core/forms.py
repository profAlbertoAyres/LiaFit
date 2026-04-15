from django import forms
from django.db.models import QuerySet


class BaseModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        self.professional = kwargs.pop('professional', None)

        super().__init__(*args, **kwargs)

        self._apply_tenant_filter()
        self._apply_bootstrap_styles()

    # -------------------------
    # TENANT FILTER (SAAS CORE)
    # -------------------------
    def _apply_tenant_filter(self):
        if not self.tenant:
            return

        for field in self.fields.values():
            if hasattr(field, 'queryset') and isinstance(field.queryset, QuerySet):
                model = field.queryset.model

                if hasattr(model, 'organization') or any(
                    f.name == 'organization' for f in model._meta.fields
                ):
                    field.queryset = field.queryset.filter(
                        organization=self.tenant
                    )

    # -------------------------
    # UI / BOOTSTRAP LAYER
    # -------------------------
    def _apply_bootstrap_styles(self):

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
                css_class = 'form-control'

            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'

            elif isinstance(field.widget, (
                forms.CheckboxInput,
                forms.CheckboxSelectMultiple
            )):
                css_class = 'form-check-input'

            elif isinstance(field.widget, forms.ClearableFileInput):
                css_class = 'form-control'

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
                    forms.CheckboxSelectMultiple
                ))
            ):
                label_text = field.label or field_name.replace('_', ' ').capitalize()
                field.widget.attrs['placeholder'] = str(label_text).replace(':', '')

            if field.required:
                field.widget.attrs['required'] = True

            if field_name == 'email':
                field.widget.attrs['autocomplete'] = 'email'