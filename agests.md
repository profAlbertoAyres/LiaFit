# Contexto do Projeto: LiaFit (SaaS Multi-Tenant)

## 1. Visão Geral
LiaFit é um sistema SaaS (Software as a Service) focado no segmento fitness e de saúde (academias, clínicas, estúdios). O sistema utiliza uma arquitetura **Multi-Tenant**, onde cada cliente opera dentro de uma `Organization` (Tenant) isolada, garantindo que dados (alunos, treinos, finanças) de uma empresa não vazem para outra.

## 2. Arquitetura Core: Formulários (`core/forms.py`)
Para garantir consistência visual (DRY) e segurança (isolamento de Tenant), centralizamos a lógica base de formulários no app `core`. Todos os formulários do sistema devem herdar destas classes base, e **nunca** diretamente do Django padrão.

### Código do `core/forms.py`
```python
from django import forms
from django.db.models import QuerySet

class BootstrapStyleMixin:
    """
    Injeta dinamicamente classes do Bootstrap (form-control, form-select), 
    placeholders baseados em labels e atributos HTML essenciais.
    """
    def _apply_bootstrap_styles(self):
        for field_name, field in self.fields.items():
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True

            # Definição de classes CSS baseadas no tipo de Widget
            if isinstance(field.widget, (
                forms.TextInput, forms.NumberInput, forms.EmailInput,
                forms.DateInput, forms.Textarea, forms.URLInput, forms.PasswordInput,
            )):
                css_class = 'form-control'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.ClearableFileInput):
                css_class = 'form-control'
            else:
                css_class = ''

            # Mescla as classes geradas com as já existentes
            existing = field.widget.attrs.get('class', '')
            classes = set(existing.split())
            if css_class:
                classes.add(css_class)
            field.widget.attrs['class'] = ' '.join(classes)

            # Gera placeholder automático se não existir
            if (
                not field.widget.attrs.get('placeholder') and
                not isinstance(field.widget, (forms.Select, forms.ClearableFileInput, forms.CheckboxInput, forms.CheckboxSelectMultiple))
            ):
                label_text = field.label or field_name.replace('_', ' ').capitalize()
                field.widget.attrs['placeholder'] = str(label_text).replace(':', '')

            # Atributos nativos do HTML5
            if field.required:
                field.widget.attrs['required'] = True
            if field_name == 'email':
                field.widget.attrs['autocomplete'] = 'email'

class BaseForm(BootstrapStyleMixin, forms.Form):
    """
    Para formulários soltos (Serviços, Autenticação, Onboarding, Contato).
    Garante o estilo Bootstrap automaticamente.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_styles()

class BaseModelForm(BootstrapStyleMixin, forms.ModelForm):
    """
    Para formulários atrelados a Models (CRUD).
    Aplica o visual Bootstrap E filtra ForeignKeys para o Tenant atual.
    """
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        self.professional = kwargs.pop('professional', None)
        super().__init__(*args, **kwargs)
        self._apply_tenant_filter()
        self._apply_bootstrap_styles()

    def _apply_tenant_filter(self):
        if not self.tenant:
            return
        for field in self.fields.values():
            if hasattr(field, 'queryset') and isinstance(field.queryset, QuerySet):
                model = field.queryset.model
                if hasattr(model, 'organization') or any(f.name == 'organization' for f in model._meta.fields):
                    field.queryset = field.queryset.filter(organization=self.tenant)
