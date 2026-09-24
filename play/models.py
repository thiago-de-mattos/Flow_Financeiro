from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    """Progresso do usuário em uma fase."""
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name="lesson_progress")
    lesson       = models.ForeignKey("content.Lesson", on_delete=models.CASCADE,
                                     related_name="progress")
    completed    = models.BooleanField("Concluída", default=False)
    score        = models.PositiveSmallIntegerField("Acertos", default=0)
    lives_left   = models.PositiveSmallIntegerField("Vidas restantes", default=2)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progresso na fase"
        verbose_name_plural = "Progressos nas fases"
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{'✓' if self.completed else '…'} {self.user.name} → {self.lesson.title}"


class QuestionProgress(models.Model):
    """Pergunta já respondida corretamente. Garante recompensa única."""
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="question_progress")
    question    = models.ForeignKey("content.Question", on_delete=models.CASCADE,
                                    related_name="answered_by")
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pergunta respondida"
        verbose_name_plural = "Perguntas respondidas"
        unique_together = ("user", "question")