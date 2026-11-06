# play/models.py
from django.conf import settings
from django.db import models


class LessonProgress(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name="lesson_progress")
    lesson       = models.ForeignKey("content.Lesson", on_delete=models.CASCADE,
                                     related_name="progress")
    completed    = models.BooleanField("Concluída", default=False)
    rewarded     = models.BooleanField("Bônus de fase já pago", default=False)
    score        = models.PositiveSmallIntegerField("Acertos na tentativa", default=0)
    lives_left   = models.PositiveSmallIntegerField("Vidas restantes", default=2)
    attempts     = models.PositiveSmallIntegerField("Tentativas", default=1)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progresso na fase"
        verbose_name_plural = "Progressos nas fases"
        unique_together = ("user", "lesson")

    def __str__(self):
        return f"{'✓' if self.completed else '…'} {self.user.name} → {self.lesson.title}"


class QuestionProgress(models.Model):
    """Uma linha por pergunta que o usuário já acertou alguma vez.

    solved   → conta para a tentativa atual (zera no game over)
    rewarded → XP e moedas já foram creditados (nunca zera)
    """
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="question_progress")
    question    = models.ForeignKey("content.Question", on_delete=models.CASCADE,
                                    related_name="answered_by")
    solved      = models.BooleanField("Acertou na tentativa atual", default=True)
    rewarded    = models.BooleanField("Já recebeu recompensa", default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pergunta respondida"
        verbose_name_plural = "Perguntas respondidas"
        unique_together = ("user", "question")