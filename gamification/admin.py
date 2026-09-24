# gamification/admin.py
from django.contrib import admin

from .models import Badge, LeaderboardEntry, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "category")
    list_filter  = ("category",)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "earned_at")
    list_filter  = ("badge",)


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ("rank", "user", "coins", "scope", "period")
    list_filter  = ("scope", "period")