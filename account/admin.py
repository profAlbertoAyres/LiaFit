# account/admin.py

from django.contrib import admin
from account.models import OnboardingToken


@admin.register(OnboardingToken)
class OnboardingTokenAdmin(admin.ModelAdmin):
    list_display = (
        'token_short', 'user', 'purpose', 'organization',
        'created_at', 'expires_at', 'used_at', 'status',
    )
    list_filter = ('purpose', 'used_at', 'expires_at')
    search_fields = ('user__email', 'token', 'organization__company_name')
    readonly_fields = (
        'token', 'created_at', 'created_ip', 'created_ua',
        'used_at', 'used_ip', 'used_ua',
    )
    fieldsets = (
        ('Identificação', {
            'fields': ('token', 'user', 'organization', 'purpose')
        }),
        ('Validade', {
            'fields': ('expires_at', 'data')
        }),
        ('Auditoria — Criação', {
            'fields': ('created_at', 'created_ip', 'created_ua'),
            'classes': ('collapse',),
        }),
        ('Auditoria — Uso', {
            'fields': ('used_at', 'used_ip', 'used_ua'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Token')
    def token_short(self, obj):
        return f"{str(obj.token)[:8]}…"

    @admin.display(description='Status')
    def status(self, obj):
        if obj.is_used:
            return '✅ Usado'
        if obj.is_expired:
            return '⏱️ Expirado'
        return '🟢 Válido'

from django.contrib import admin
from .models import Organization, OrganizationMember

from django.contrib import admin
from .models import Organization, OrganizationMember

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    # Removi os campos 'name' e prepopulated para não dar erro
    list_display = ('id', 'slug', 'is_active')
    search_fields = ('slug',)
    list_filter = ('is_active',)

@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    # Removi 'role' e 'autocomplete_fields' para não dar erro
    list_display = ('id', 'user', 'organization', 'is_active')
    list_filter = ('is_active', 'organization')
