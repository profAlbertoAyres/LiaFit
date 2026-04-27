from django import forms
from django.db.models import QuerySet


class LiaFitStyleMixin:
    def _apply_liafit_styles(self):
        for field_name, field in self.fields.items():

            # Localização de decimais (vírgula/ponto)
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True

            # Define a classe CSS do LiaFit com filters no tipo de widget
            if isinstance(field.widget, (
                    forms.TextInput,
                    forms.NumberInput,
                    forms.EmailInput,
                    forms.DateInput,
                    forms.Textarea,
                    forms.URLInput,
                    forms.PasswordInput,
            )):
                css_class = 'lia-form-control'  # ← Mudou aqui

            elif isinstance(field.widget, forms.Select):
                css_class = 'lia-form-control'  # ← Mudou aqui (Selects usam a mesma filters visual)

            elif isinstance(field.widget, (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple
            )):
                # Mantemos o form-check-input do Bootstrap aqui pois
                # a animação do Switch de ligar/desligar depende dele
                css_class = 'form-check-input'

            elif isinstance(field.widget, forms.ClearableFileInput):
                css_class = 'lia-form-control'  # ← Mudou aqui

            else:
                css_class = ''

            # Adiciona a classe CSS sem sobrescrever classes que você já tenha passado manualmente
            existing = field.widget.attrs.get('class', '')
            classes = set(existing.split())
            if css_class:
                classes.add(css_class)
            field.widget.attrs['class'] = ' '.join(classes)

            # Gera Placeholder automático baseado no Label (se não existir um)
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

            # Atributos nativos do HTML
            if field.required:
                field.widget.attrs['required'] = True

            if field_name == 'email':
                field.widget.attrs['autocomplete'] = 'email'


class BaseForm(LiaFitStyleMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        # Captura kwargs de contexto SaaS (ficam disponíveis como self.tenant etc.)
        self.tenant       = kwargs.pop('tenant', None)
        self.membership   = kwargs.pop('membership', None)
        self.professional = kwargs.pop('professional', None)

        super().__init__(*args, **kwargs)
        self._apply_liafit_styles()


class BaseModelForm(LiaFitStyleMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        self.membership = kwargs.pop('membership', None) # <-- ADICIONE ESTA LINHA
        self.professional = kwargs.pop('professional', None)

        super().__init__(*args, **kwargs)

        # Aplica os filtros de segurança do SaaS e depois o visual
        self._apply_tenant_filter()
        self._apply_liafit_styles()  # ← Atualizou a chamada do método

    def _apply_tenant_filter(self):
        if not self.tenant:
            return

        for field in self.fields.values():
            if hasattr(field, 'queryset') and isinstance(field.queryset, QuerySet):
                model = field.queryset.model

                # Verifica se o modelo relacionado tem o campo 'organization'
                if hasattr(model, 'organization') or any(
                        f.name == 'organization' for f in model._meta.fields
                ):
                    field.queryset = field.queryset.filter(
                        organization=self.tenant
                    )
