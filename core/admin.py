# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ("name", "email", "age", "is_active", "is_staff", "created_at")
    search_fields   = ("name", "email")
    ordering        = ("name",)
    readonly_fields = ("age", "created_at", "last_login")
    fieldsets = (
        (None,         {"fields": ("email", "password")}),
        ("Dados",      {"fields": ("name", "birth_date", "age", "created_at", "last_login")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",),
                "fields": ("email", "name", "birth_date", "password1", "password2")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display    = ("user", "level", "xp_total", "coins", "streak_days", "last_activity")
    search_fields   = ("user__name", "user__email")
    readonly_fields = ("xp_total", "xp_next_level", "level", "coins", "streak_days")