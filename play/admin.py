# play/admin.py
from django.contrib import admin

from .models import LessonProgress, QuestionProgress


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "score", "lives_left", "completed_at")
    list_filter  = ("completed", "lesson__module")
    search_fields = ("user__name", "user__email")


@admin.register(QuestionProgress)
class QuestionProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "answered_at")
    search_fields = ("user__name",)