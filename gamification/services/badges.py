from play.models import LessonProgress, QuestionProgress

from ..models import Badge, UserBadge

DEFAULT_BADGES = [
    {"title": "Primeiros Passos",  "description": "Responda sua primeira pergunta",
     "icon": "first_step",     "category": "progress"},
    {"title": "Poupador",          "description": "Junte 100 moedas",
     "icon": "save",           "category": "financial"},
    {"title": "Organizado",        "description": "Complete sua primeira fase",
     "icon": "budgeter",       "category": "progress"},
    {"title": "Investidor",        "description": "Complete 3 fases",
     "icon": "investor",       "category": "progress"},
    {"title": "Sequência Master",  "description": "7 dias seguidos de acesso",
     "icon": "streak_master",  "category": "streak"},
    {"title": "Finance Pro",       "description": "Responda 25 perguntas",
     "icon": "finance_pro",    "category": "progress"},
]


def ensure_default_badges(overwrite=False):
    """Cria os badges que faltam. Com overwrite=True, também ressincroniza
    título, descrição e categoria com os valores do código."""
    for badge in DEFAULT_BADGES:
        if overwrite:
            Badge.objects.update_or_create(icon=badge["icon"], defaults=badge)
        else:
            Badge.objects.get_or_create(icon=badge["icon"], defaults=badge)


def award_eligible_badges(user, profile=None):
    ensure_default_badges()
    profile = profile or user.profile
    respondidas = QuestionProgress.objects.filter(user=user).count()
    fases = LessonProgress.objects.filter(user=user, completed=True).count()

    regras = {
        "first_step":    respondidas >= 1,
        "save":          profile.coins >= 100,
        "budgeter":      fases >= 1,
        "investor":      fases >= 3,
        "streak_master": profile.streak_days >= 7,
        "finance_pro":   respondidas >= 25,
    }

    ganhos = []
    for icon, liberado in regras.items():
        if not liberado:
            continue
        badge = Badge.objects.filter(icon=icon).first()
        if badge is None:
            continue
        user_badge, criado = UserBadge.objects.get_or_create(user=user, badge=badge)
        if criado:
            ganhos.append(user_badge)
    return ganhos