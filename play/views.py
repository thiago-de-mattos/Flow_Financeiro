# play/views.py
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from content.models import Lesson, Question

from .models import LessonProgress, QuestionProgress
from .services.play import responder


@login_required
def play_view(request):
    """Trilha: uma parada por fase, com o estado de cada uma."""
    user = request.user

    concluidas = set(
        LessonProgress.objects.filter(user=user, completed=True)
        .values_list("lesson_id", flat=True)
    )
    acertos = dict(
        QuestionProgress.objects.filter(user=user, solved=True)
        .values_list("question__lesson_id")
        .annotate(n=Count("id"))
    )

    trilha, atual_marcada = [], False
    for fase in Lesson.objects.select_related("module").annotate(total=Count("questions")):
        if fase.id in concluidas:
            estado = "done"
        elif not atual_marcada:
            estado, atual_marcada = "current", True
        else:
            estado = "locked"
        trilha.append({
            "fase": fase,
            "estado": estado,
            "acertos": acertos.get(fase.id, 0),
            "total": fase.total,
        })

    return render(request, "play.html", {"trilha": trilha, "profile": user.profile})


@login_required
@require_POST
def answer_view(request):
    try:
        dados = json.loads(request.body.decode("utf-8"))
        question_id = int(dados["question_id"])
        resposta = dados["answer"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"error": "Resposta inválida."}, status=400)

    try:
        question = Question.objects.select_related("lesson").get(pk=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"error": "Pergunta não encontrada."}, status=404)

    res = responder(request.user, question, resposta)
    profile = request.user.profile

    return JsonResponse({
        "acertou":        res.acertou,
        "explicacao":     res.explicacao,
        "vidas":          res.vidas_restantes,
        "game_over":      res.game_over,
        "fase_concluida": res.fase_concluida,
        "respondidas":    res.respondidas,
        "total":          res.total,
        "recompensa":     {"xp": res.xp, "moedas": res.moedas},
        "badges":         res.badges,
        "profile": {
            "coins":         profile.coins,
            "level":         profile.level,
            "xp_total":      profile.xp_total,
            "xp_next_level": profile.xp_next_level,
        },
    })