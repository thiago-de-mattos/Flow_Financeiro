# content/admin.py
from django.contrib import admin

from .models import Lesson, Module, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("order_index", "kind", "statement", "payload", "explanation", "xp_reward", "coins_reward")


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("order_index", "title", "topic")
    show_change_link = True


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("order_index", "title", "is_active", "total_fases")
    list_editable = ("is_active",)
    inlines = [LessonInline]

    @admin.display(description="Fases")
    def total_fases(self, obj):
        return obj.lessons.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("order_index", "title", "module", "topic", "total_perguntas")
    list_filter  = ("module",)
    search_fields = ("title", "topic")
    inlines = [QuestionInline]

    @admin.display(description="Perguntas")
    def total_perguntas(self, obj):
        return obj.questions.count()