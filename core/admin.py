from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Module, Lesson, UserLessonProgress, Badge, UserBadge, LeaderboardEntry


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ("name", "email", "age", "is_active", "is_staff", "created_at")
    search_fields = ("name", "email")
    ordering      = ("name",)
    fieldsets = (
        (None,           {"fields": ("email", "password")}),
        ("Dados",        {"fields": ("name", "age")}),
        ("Permissões",   {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "name", "age", "password1", "password2"),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ("user", "level", "xp_total", "coins", "streak_days", "last_activity")
    search_fields = ("user__name", "user__email")
    readonly_fields = ("xp_total", "xp_next_level", "level", "coins", "streak_days")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display  = ("order_index", "title", "is_active")
    list_editable = ("is_active",)
    ordering      = ("order_index",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display  = ("title", "module", "lesson_type", "order_index", "xp_reward", "coins_reward")
    list_filter   = ("lesson_type", "module")
    search_fields = ("title",)
    ordering      = ("module", "order_index")


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display  = ("user", "lesson", "completed", "score", "completed_at")
    list_filter   = ("completed",)
    search_fields = ("user__name", "lesson__title")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ("title", "category", "locked_by_default")
    list_filter   = ("category",)
    search_fields = ("title",)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ("user", "badge", "earned_at")
    search_fields = ("user__name", "badge__title")


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display  = ("rank", "user", "coins", "scope", "period")
    list_filter   = ("scope", "period")
    ordering      = ("scope", "period", "rank")