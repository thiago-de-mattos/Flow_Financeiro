from django.conf import settings
from django.db import models


class Badge(models.Model):
    BADGE_CATEGORIES = [
        ("progress", "Progresso"), ("streak", "Sequência"),
        ("financial", "Financeiro"), ("social", "Social"), ("special", "Especial"),
    ]
    title             = models.CharField("Título", max_length=100)
    description       = models.TextField("Descrição")
    icon              = models.CharField("Ícone", max_length=100, blank=True)
    category          = models.CharField("Categoria", max_length=20, choices=BADGE_CATEGORIES)
    locked_by_default = models.BooleanField("Bloqueada por padrão", default=True)

    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"

    def __str__(self):
        return self.title


class UserBadge(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name="badges")
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="earned_by")
    earned_at = models.DateTimeField("Conquistada em", auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")


class LeaderboardEntry(models.Model):
    SCOPES = [("global", "Global"), ("friends", "Amigos"), ("school", "Escola")]

    user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="leaderboard_entries")
    coins  = models.PositiveIntegerField(default=0)
    rank   = models.PositiveIntegerField(default=0)
    scope  = models.CharField(max_length=10, choices=SCOPES, default="global")
    period = models.DateField()

    class Meta:
        unique_together = ("user", "scope", "period")
        ordering = ["rank"]