import django_filters
from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe


class InlineRangeWidget(django_filters.widgets.RangeWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        return mark_safe(f'<div style="display: flex; gap: 10px; align-items: center; width: 100%;">{output}</div>')


class SaaSBaseFilter(django_filters.FilterSet):
    """Filtro base para o SaaS Admin, sem barreiras de Tenant."""

    search = django_filters.CharFilter(
        method='filter_search',
        label='Busca',
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar...',
        })
    )

    # Assumindo que a maioria dos models do SaaS Admin terá 'created_at'
    created_at = django_filters.DateFromToRangeFilter(
        label='Período',
        widget=InlineRangeWidget(attrs={
            'data-datepicker': '',
            'type': 'text',
            'placeholder': 'DD/MM/AAAA'
        })
    )

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, **kwargs)
        self.request = request

        # Injeta as classes CSS para o form de filtro ficar bonito no Admin
        for field in self.form.fields.values():
            existing_class = field.widget.attrs.get('class', '')
            if 'lia-form-control' not in existing_class:
                field.widget.attrs['class'] = f'{existing_class} lia-form-control'.strip()

    def filter_search(self, queryset, name, value):
        search_fields = getattr(self.Meta, 'search_fields', [])

        if not search_fields or not value:
            return queryset

        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": value})

        return queryset.filter(query).distinct()
