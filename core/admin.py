from django.contrib import admin
from django.contrib.auth import get_user_model

from core.models import (
    Module,
    ModuleItem,
    OrganizationModule,
    Permission,
    Role,
    RolePermission,
    UserPermission,
)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active", "is_core", "show_in_menu")
    list_filter = ("is_active", "is_core", "show_in_menu")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(ModuleItem)
class ModuleItemAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "slug", "order", "is_active", "show_in_menu")
    list_filter = ("module", "is_active", "show_in_menu")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("module__order", "order", "name")
    autocomplete_fields = ("module",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("codename", "name", "item", "action", "is_active")
    list_filter = ("action", "is_active", "item__module")
    search_fields = ("codename", "name", "item__name")
    autocomplete_fields = ("item",)
    readonly_fields = ("codename",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "slug", "level", "is_active")
    list_filter = ("organization", "is_active", "level")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("organization",)
    ordering = ("organization", "level", "name")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("organization", "role", "permission")
    list_filter = ("organization", "role")
    search_fields = ("role__name", "permission__codename")
    autocomplete_fields = ("organization", "role", "permission")



@admin.register(OrganizationModule)
class OrganizationModuleAdmin(admin.ModelAdmin):
    list_display = ("organization", "module", "is_active", "activated_at")
    list_filter = ("is_active", "module")
    search_fields = ("organization__company_name", "module__name")
    autocomplete_fields = ("organization", "module")
    date_hierarchy = "activated_at"
