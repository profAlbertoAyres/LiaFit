# saas_admin/filters/user_filter.py
import re

import django_filters
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.filters.base_filter import BaseFilter

User = get_user_model()


class UserFilter(BaseFilter):
    status = django_filters.ChoiceFilter(
        label=_("Status"),
        method='filter_status',
        choices=[
            ('active',    _('Ativos')),
            ('inactive',  _('Inativos')),
            ('pending',   _('Pendentes (sem senha)')),
            ('verified',  _('E-mail verificado')),
            ('unverified',_('E-mail não verificado')),
        ],
        empty_label=_("Todos"),
    )

    is_superuser = django_filters.BooleanFilter(
        label=_("Tipo"),
        widget=forms.Select(choices=[
            ('', _('Todos')),
            (True, _('Superusuários')),
            (False, _('Usuários comuns')),
        ]),
    )

    order_by = django_filters.OrderingFilter(
        label=_("Ordenar por"),
        fields=(
            ('fullname', 'name'),
            ('email', 'email'),
            ('date_joined', 'joined'),
            ('last_login', 'last_login'),
        ),
        choices=(
            ('name',         _('Nome (A-Z)')),
            ('-name',        _('Nome (Z-A)')),
            ('email',        _('E-mail (A-Z)')),
            ('-email',       _('E-mail (Z-A)')),
            ('joined',       _('Cadastro mais antigo')),
            ('-joined',      _('Cadastro mais recente')),
            ('last_login',   _('Último login (mais antigo)')),
            ('-last_login',  _('Último login (mais recente)')),
        ),
    )

    class Meta:
        model = User
        fields = ['search', 'status', 'is_superuser', 'created_at']
        search_fields = ['fullname', 'email', 'cpf', 'phone']

    # ──────────────────────────────────────────────
    # Busca com normalização de CPF / telefone
    # ──────────────────────────────────────────────
    def filter_search(self, queryset, name, value):
        if not value:
            return queryset

        text_query = (
            Q(fullname__icontains=value)
            | Q(email__icontains=value)
        )

        digits_only = re.sub(r'\D', '', value)
        if digits_only:
            text_query |= Q(cpf__icontains=digits_only)
            text_query |= Q(phone__icontains=digits_only)
        else:
            text_query |= Q(cpf__icontains=value)
            text_query |= Q(phone__icontains=value)

        return queryset.filter(text_query).distinct()

    def filter_status(self, queryset, name, value):
        if value == 'active':
            return queryset.filter(is_active=True).exclude(password='')
        if value == 'inactive':
            return queryset.filter(is_active=False)
        if value == 'pending':
            return queryset.filter(password='')
        if value == 'verified':
            return queryset.filter(email_verified_at__isnull=False)
        if value == 'unverified':
            return queryset.filter(email_verified_at__isnull=True)
        return queryset
