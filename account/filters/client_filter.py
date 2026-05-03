# account/filters/client_filter.py
import re

import django_filters
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from account.models import OrganizationClient
from core.filters.base_filter import BaseFilter


class OrganizationClientFilter(BaseFilter):
    status = django_filters.ChoiceFilter(
        label=_("Status"),
        method='filter_status',
        choices=[
            ('active',   _('Ativos')),
            ('pending',  _('Pendentes (sem senha)')),
            ('inactive', _('Inativos')),
            ('archived', _('Arquivados')),
        ],
        empty_label=_("Ativos + Pendentes + Inativos"),
    )

    order_by = django_filters.OrderingFilter(
        label=_("Ordenar por"),
        fields=(
            ('user__user__fullname', 'name'),
            ('user__user__email', 'email'),
            ('created_at', 'created'),
            ('first_service_at', 'first_service'),
        ),
        choices=(
            ('name', _('Nome (A-Z)')),
            ('-name', _('Nome (Z-A)')),
            ('email', _('E-mail (A-Z)')),
            ('-email', _('E-mail (Z-A)')),
            ('created', _('Cadastro mais antigo')),
            ('-created', _('Cadastro mais recente')),
            ('first_service', _('Primeiro atendimento (mais antigo)')),
            ('-first_service', _('Primeiro atendimento (mais recente)')),
        ),
    )
    class Meta:
        model = OrganizationClient
        fields = ['search', 'status', 'created_at' ]
        search_fields = [
            'user__user__fullname',
            'user__user__email',
            'user__user__cpf',
            'user__user__phone',
        ]

    # ───────────────────────────────────────────────────────────
    # OVERRIDE: filter_search com normalização de CPF/telefone
    # ───────────────────────────────────────────────────────────
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        # 1) Busca textual normal (nome, email com o termo cru)
        text_query = (
            Q(user__user__fullname__icontains=value)
            | Q(user__user__email__icontains=value)
        )

        # 2) Versão só-números do termo digitado
        digits_only = re.sub(r'\D', '', value)

        # 3) Se sobraram dígitos, casa contra CPF/telefone (que estão sem máscara no banco)
        if digits_only:
            text_query |= Q(user__user__cpf__icontains=digits_only)
            text_query |= Q(user__user__phone__icontains=digits_only)
        else:
            # Se não tinha dígitos, ainda assim tenta casar por CPF/telefone literal
            text_query |= Q(user__user__cpf__icontains=value)
            text_query |= Q(user__user__phone__icontains=value)

        return queryset.filter(text_query).distinct()

    # ───────────────────────────────────────────────────────────
    # FILTRO CUSTOMIZADO: STATUS (lógica)
    # ───────────────────────────────────────────────────────────
    def filter_status(self, queryset, name, value):

        if value == 'active':
            return queryset.filter(
                archived_at__isnull=True,
                user__user__is_active=True,
            ).exclude(user__user__password='')

        if value == 'pending':
            return queryset.filter(
                archived_at__isnull=True,
                user__user__password='',
            )

        if value == 'inactive':
            return queryset.filter(
                archived_at__isnull=True,
                user__user__is_active=False,
            ).exclude(user__user__password='')

        if value == 'archived':
            return queryset.filter(archived_at__isnull=False)

        # Default (empty_label selecionado): esconde arquivados
        return queryset.filter(archived_at__isnull=True)


