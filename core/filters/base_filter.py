# core/filters/base_filter.py
import django_filters
from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe


class InlineRangeWidget(django_filters.widgets.RangeWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        return mark_safe(f'<div style="display: flex; gap: 10px; align-items: center; width: 100%;">{output}</div>')


class BaseFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method='filter_search',
        label='Busca',
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar...',
        })
    )

    created_at = django_filters.DateFromToRangeFilter(
        label='Período',
        widget=InlineRangeWidget(attrs={
            'data-datepicker': '',
            'type': 'text',
            'placeholder': 'DD/MM/AAAA'
        })
    )

    order_by = django_filters.OrderingFilter(fields=[], field_labels={})

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, **kwargs)

        self.request = request
        self.organization = getattr(request, "context", None) and getattr(request.context, "organization", None)

        if self.organization and queryset is not None:
            model = queryset.model
            if hasattr(model, "organization"):
                self.queryset = queryset.filter(organization=self.organization)

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
