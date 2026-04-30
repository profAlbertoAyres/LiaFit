# account/filters/member_filter.py
import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _

from core.filters.base_filter import BaseFilter, InlineRangeWidget
from core.models import Role
from account.models import OrganizationMember, Specialty
from account.models.member import RemunerationType


class OrganizationMemberFilter(BaseFilter):
    # ───────────────────────────────────────────────────────────
    # FILTROS DIRETOS
    # ───────────────────────────────────────────────────────────
    roles = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.none(),
        label=_("Cargos"),
        widget=forms.SelectMultiple(attrs={'size': '1'}),
    )

    is_active = django_filters.BooleanFilter(
        label=_("Ativo"),
        widget=forms.Select(choices=[
            ('', _('Todos')),
            (True, _('Ativos')),
            (False, _('Inativos')),
        ]),
    )

    remuneration_type = django_filters.ChoiceFilter(
        choices=RemunerationType.choices,
        label=_("Tipo de Remuneração"),
        empty_label=_("Todos os Tipos"),
    )

    joined_at = django_filters.DateFromToRangeFilter(
        label=_("Período de Admissão"),
        widget=InlineRangeWidget(attrs={
            'data-datepicker': '',       # Aciona seu Flatpickr nos dois inputs gerados
            'type': 'text',              # Impede conflito com calendário nativo
            'placeholder': 'dd/mm/aaaa',
        }),
    )

    # ───────────────────────────────────────────────────────────
    # FILTROS CUSTOM
    # ───────────────────────────────────────────────────────────
    has_left = django_filters.ChoiceFilter(
        label=_("Situação"),
        method='filter_has_left',
        choices=[
            ('active', _('Apenas Ativos (não desligados)')),
            ('left', _('Apenas Desligados')),
        ],
        empty_label=_("Todos"),
    )

    profile_type = django_filters.ChoiceFilter(
        label=_("Tipo de Perfil"),
        method='filter_profile_type',
        choices=[
            ('professional', _('Profissional')),
            ('assistant', _('Assistente')),
            ('none', _('Sem Perfil')),
        ],
        empty_label=_("Todos os Perfis"),
    )

    specialty = django_filters.ModelChoiceFilter(
        queryset=Specialty.objects.filter(is_active=True),
        label=_("Especialidade"),
        empty_label=_("Todas as Especialidades"),
        method='filter_specialty',
    )

    # ───────────────────────────────────────────────────────────
    # META
    # ───────────────────────────────────────────────────────────
    class Meta:
        model = OrganizationMember
        fields = [
            'roles',
            'is_active',
            'remuneration_type',
            'joined_at',
            'has_left',
            'profile_type',
            'specialty',
        ]
        # 🔥 AQUI ESTAVA O SEGREDO DA BUSCA 🔥
        # Como no seu model User "first_name = None", mudamos para "user__fullname".
        search_fields = [
            'user__email',
            'user__fullname',
        ]

    # ───────────────────────────────────────────────────────────
    # INIT
    # ───────────────────────────────────────────────────────────
    def __init__(self, data=None, queryset=None, *, request=None, **kwargs):
        super().__init__(data=data, queryset=queryset, request=request, **kwargs)
        if self.organization:
            self.form.fields['roles'].queryset = Role.objects.filter(
                organization=self.organization
            )

    def filter_has_left(self, queryset, name, value):
        if value == 'active':
            return queryset.filter(left_at__isnull=True)
        if value == 'left':
            return queryset.filter(left_at__isnull=False)
        return queryset

    def filter_profile_type(self, queryset, name, value):
        if value == 'professional':
            return queryset.filter(professional_profile__isnull=False)
        if value == 'assistant':
            return queryset.filter(assistant_profile__isnull=False)
        if value == 'none':
            return queryset.filter(
                professional_profile__isnull=True,
                assistant_profile__isnull=True,
            )
        return queryset

    def filter_specialty(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            professional_profile__specialties=value
        ).distinct()
