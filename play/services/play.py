# play/services/play.py
from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from gamification.services.badges import award_eligible_badges

from ..models import LessonProgress, QuestionProgress

VIDAS_POR_FASE = 2


@dataclass
class Resultado:
    acertou: bool
    explicacao: str = ""
    vidas_restantes: int = VIDAS_POR_FASE
    game_over: bool = False
    fase_concluida: bool = False
    respondidas: int = 0
    total: int = 0
    xp: int = 0
    moedas: int = 0
    badges: list = field(default_factory=list)


@transaction.atomic
def responder(user, question, resposta) -> Resultado:
    lesson = question.lesson
    progresso, _ = LessonProgress.objects.select_for_update().get_or_create(
        user=user, lesson=lesson, defaults={"lives_left": VIDAS_POR_FASE},
    )
    profile = user.profile
    total = lesson.questions.count()
    res = Resultado(acertou=False, explicacao=question.explanation, total=total)

    if question.check_answer(resposta):
        res.acertou = True
        registro, _ = QuestionProgress.objects.get_or_create(user=user, question=question)
        registro.solved = True

        if not registro.rewarded:                      # paga UMA vez na vida
            res.xp, res.moedas = question.xp_reward, question.coins_reward
            profile.coins += question.coins_reward
            profile.add_xp(question.xp_reward)
            profile.update_streak()
            registro.rewarded = True

        registro.save(update_fields=["solved", "rewarded"])
    else:
        progresso.lives_left = max(0, progresso.lives_left - 1)

        if progresso.lives_left == 0:                  # zera a fase, mantém o pagamento
            res.game_over = True
            QuestionProgress.objects.filter(
                user=user, question__lesson=lesson
            ).update(solved=False)
            progresso.lives_left = VIDAS_POR_FASE
            progresso.attempts += 1

    res.respondidas = QuestionProgress.objects.filter(
        user=user, question__lesson=lesson, solved=True
    ).count()

    if res.respondidas >= total and not progresso.completed:
        progresso.completed = True
        progresso.completed_at = timezone.now()
        res.fase_concluida = True

        if not progresso.rewarded:                     # bônus de fase também é único
            res.xp += lesson.xp_reward
            res.moedas += lesson.coins_reward
            profile.coins += lesson.coins_reward
            profile.add_xp(lesson.xp_reward)
            progresso.rewarded = True

    progresso.score = res.respondidas
    progresso.save()

    res.vidas_restantes = progresso.lives_left
    res.badges = [
        {"title": ub.badge.title, "icon": ub.badge.icon}
        for ub in award_eligible_badges(user, profile)
    ]
    return res