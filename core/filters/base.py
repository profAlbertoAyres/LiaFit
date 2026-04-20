import django_filters
from django import forms
from django.db.models import Q


class BaseFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(
        method='filter_search',
        label='Busca',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar...',
        })
    )

    created_at = django_filters.DateFromToRangeFilter(
        label='Período',
        widget=django_filters.widgets.RangeWidget(attrs={
            'class': 'form-control date-picker',
            'readonly': 'readonly',
        })
    )

    order_by = django_filters.OrderingFilter(fields=[], field_labels={})

    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, **kwargs)

        self.request = request
        self.organization = getattr(request, "context", None) and getattr(request.context, "organization", None)

        # 🔥 FILTRO MULTI-TENANT REAL (DATA LAYER)
        if self.organization and queryset is not None:
            model = queryset.model
            if hasattr(model, "organization"):
                self.queryset = queryset.filter(organization=self.organization)

        # UI improvements (mantido)
        for field in self.form.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.TextInput):
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs.update({'class': f'{existing} form-control'.strip()})

    def filter_search(self, queryset, name, value):
        search_fields = getattr(self.Meta, 'search_fields', [])

        if not search_fields or not value:
            return queryset

        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": value})

        return queryset.filter(query).distinct()