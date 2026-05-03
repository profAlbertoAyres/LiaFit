# core/filters/role_filter.py
import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _

from core.filters.base_filter import BaseFilter
from core.models import Role


class RoleFilter(BaseFilter):

    is_active = django_filters.BooleanFilter(
        label=_("Situação"),
        widget=forms.Select(choices=[
            ('', _('Todos')),
            (True, _('Ativos')),
            (False, _('Inativos')),
        ]),
    )

    level = django_filters.RangeFilter(
        label=_("Nível"),
    )


    has_members = django_filters.ChoiceFilter(
        label=_("Vínculo com membros"),
        method='filter_has_members',
        choices=[
            ('with', _('Com membros')),
            ('without', _('Sem membros')),
        ],
        empty_label=_("Todos"),
    )


    order_by = django_filters.OrderingFilter(
        label=_("Ordenar por"),
        fields=(
            ('name', 'name'),
            ('level', 'level'),
        ),
        choices=(
            ('name', _('Nome (A-Z)')),
            ('-name', _('Nome (Z-A)')),
            ('level', _('Nível (menor → maior)')),
            ('-level', _('Nível (maior → menor)')),
        ),
    )

    # ───────────────────────────────────────────────────────────
    # META
    # ───────────────────────────────────────────────────────────
    class Meta:
        model = Role
        fields = [
            'search',
            'is_active',
            'level',
            'has_members',
        ]
        search_fields = [
            'name',
            'slug',
            'description',
        ]

    # ───────────────────────────────────────────────────────────
    # MÉTODOS CUSTOM
    # ───────────────────────────────────────────────────────────
    def filter_has_members(self, queryset, name, value):
        if value == 'with':
            return queryset.filter(members__isnull=False).distinct()
        if value == 'without':
            return queryset.filter(members__isnull=True)
        return queryset
