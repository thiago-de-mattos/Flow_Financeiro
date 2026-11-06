import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from content.models import Lesson, Question
from core.models import Profile

from .models import LessonProgress, QuestionProgress
from .services.play import VIDAS_POR_FASE, responder


def fases_da_trilha():
    return (
        Lesson.objects
        .filter(module__is_active=True)
        .select_related("module")
        .annotate(total_perguntas=Count("questions"))
        .filter(total_perguntas__gte=5)
        .order_by("module__order_index", "module_id", "order_index", "pk")
    )


def primeira_fase_disponivel(usuario):
    fases_concluidas = LessonProgress.objects.filter(
        user=usuario,
        completed=True,
    ).values_list("lesson_id", flat=True)

    return fases_da_trilha().exclude(pk__in=fases_concluidas).first()


def perguntas_pendentes(usuario, fase):
    perguntas_acertadas = QuestionProgress.objects.filter(
        user=usuario,
        question__lesson=fase,
        solved=True,
    ).values_list("question_id", flat=True)

    return (
        fase.questions
        .exclude(pk__in=perguntas_acertadas)
        .order_by("order_index", "pk")
    )


@login_required
def play_view(request):
    usuario = request.user

    progressos = {
        progresso.lesson_id: progresso
        for progresso in LessonProgress.objects.filter(user=usuario)
    }

    trilha = []
    quantidade_concluida = 0
    fase_atual_encontrada = False

    for fase in fases_da_trilha():
        progresso = progressos.get(fase.pk)

        if progresso and progresso.completed:
            estado = "done"
            quantidade_concluida += 1
        elif not fase_atual_encontrada:
            estado = "current"
            fase_atual_encontrada = True
        else:
            estado = "locked"

        trilha.append({
            "fase": fase,
            "estado": estado,
            "acertos": progresso.score if progresso else 0,
            "total": fase.total_perguntas,
        })

    return render(request, "play.html", {
        "trilha": trilha,
        "concluidas": quantidade_concluida,
        "profile": usuario.profile,
    })


@login_required
def fase_view(request, fase_id):
    usuario = request.user
    fase = get_object_or_404(fases_da_trilha(), pk=fase_id)

    progresso = LessonProgress.objects.filter(
        user=usuario,
        lesson=fase,
    ).first()

    concluida = bool(progresso and progresso.completed)

    if not concluida and fase != primeira_fase_disponivel(usuario):
        return redirect("play")

    pergunta = None
    numero = fase.total_perguntas
    opcoes = []
    termos = []
    definicoes = []

    if not concluida:
        pendentes = perguntas_pendentes(usuario, fase)
        pergunta = pendentes.first()
        numero = fase.total_perguntas - pendentes.count() + 1

        if pergunta and pergunta.kind == Question.KIND_MC:
            opcoes = pergunta.payload["options"]

        elif pergunta and pergunta.kind == Question.KIND_MATCH:
            pares = pergunta.payload["pairs"]
            termos = [termo for termo, definicao in pares]
            definicoes = sorted({definicao for termo, definicao in pares})

    return render(request, "fase.html", {
        "fase": fase,
        "concluida": concluida,
        "pergunta": pergunta,
        "numero": numero,
        "total": fase.total_perguntas,
        "vidas_restantes": progresso.lives_left if progresso else VIDAS_POR_FASE,
        "total_vidas": VIDAS_POR_FASE,
        "espacos_vidas": range(1, VIDAS_POR_FASE + 1),
        "opcoes": opcoes,
        "termos": termos,
        "definicoes": definicoes,
    })


@login_required
@require_POST
@transaction.atomic
def answer_view(request):
    try:
        dados = json.loads(request.body)
        pergunta_id = dados["question_id"]
        resposta = dados["answer"]
    except (ValueError, TypeError, KeyError):
        return JsonResponse({"error": "Resposta inválida."}, status=400)

    if type(pergunta_id) is not int or not 0 < pergunta_id <= 2**63 - 1:
        return JsonResponse({"error": "Identificador inválido."}, status=400)

    # Serializa os envios da mesma conta em bancos que suportam bloqueio de linha.
    perfil = get_object_or_404(
        Profile.objects.select_for_update(),
        user=request.user,
    )

    fase = primeira_fase_disponivel(request.user)

    if fase is None:
        return JsonResponse({"error": "A trilha já foi concluída."}, status=409)

    pergunta = perguntas_pendentes(request.user, fase).first()

    if pergunta is None or pergunta.pk != pergunta_id:
        return JsonResponse({
            "error": "O progresso mudou. Reabra a fase para continuar."
        }, status=409)

    resultado = responder(request.user, pergunta, resposta)
    perfil.refresh_from_db()

    return JsonResponse({
        "acertou": resultado.acertou,
        "explicacao": resultado.explicacao,
        "vidas": resultado.vidas_restantes,
        "game_over": resultado.game_over,
        "fase_concluida": resultado.fase_concluida,
        "respondidas": resultado.respondidas,
        "total": resultado.total,
        "recompensa": {
            "xp": resultado.xp,
            "moedas": resultado.moedas,
        },
        "badges": resultado.badges,
        "profile": {
            "coins": perfil.coins,
            "level": perfil.level,
            "xp_total": perfil.xp_total,
            "xp_next_level": perfil.xp_next_level,
        },
    })