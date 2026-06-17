from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .forms import RegisterForm, LoginForm
from .models import Profile


# ─── Autenticação ─────────────────────────────────────────────────────────────

def inicio_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    return render(request, "inicio.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            Profile.objects.get_or_create(user=user)

        login(request, user)
        return redirect("home")

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("inicio")


# ─── Páginas principais ───────────────────────────────────────────────────────

@login_required
def home_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.update_streak()

    return render(request, "home.html", {
        "profile": profile
    })


@login_required
def play_view(request):
    from .models import Module, UserLessonProgress

    modules = Module.objects.filter(is_active=True).prefetch_related("lessons")

    progress = UserLessonProgress.objects.filter(
        user=request.user,
        completed=True
    ).values_list("lesson_id", flat=True)

    return render(request, "play.html", {
        "modules": modules,
        "progress": set(progress),
    })


@login_required
def profile_view(request):
    from .models import UserBadge, UserLessonProgress

    profile, created = Profile.objects.get_or_create(user=request.user)

    # Salva avatar escolhido
    avatares_validos = ["pessoa1","pessoa2","pessoa3","pessoa4","pessoa5","pessoa6"]
    if request.method == "POST":
        avatar = request.POST.get("avatar")
        if avatar in avatares_validos:
            profile.avatar = avatar
            profile.save()
        return redirect("profile")

    badges       = UserBadge.objects.filter(user=request.user).select_related("badge")
    lessons_done = UserLessonProgress.objects.filter(user=request.user, completed=True).count()

    return render(request, "profile.html", {
        "profile":      profile,
        "badges":       badges,
        "lessons_done": lessons_done,
        "avatares":     avatares_validos,
    })


@login_required
def achievements_view(request):
    from .models import Badge, UserBadge

    earned_ids = UserBadge.objects.filter(
        user=request.user
    ).values_list("badge_id", flat=True)

    badges = Badge.objects.all()

    return render(request, "achievements.html", {
        "badges": badges,
        "earned_ids": set(earned_ids),
    })


@login_required
def leaderboard_view(request):
    from .models import LeaderboardEntry
    from django.utils import timezone
    import datetime

    scope  = request.GET.get("scope", "global")
    period = timezone.localdate()
    period = period - datetime.timedelta(days=period.weekday())

    entries = LeaderboardEntry.objects.filter(
        scope=scope, period=period
    ).select_related("user").order_by("rank")

    # Entrada do usuário logado
    try:
        user_entry = LeaderboardEntry.objects.get(
            user=request.user, scope=scope, period=period
        )
    except LeaderboardEntry.DoesNotExist:
        user_entry = None

    return render(request, "leaderboard.html", {
        "entries":    entries,
        "scope":      scope,
        "user_entry": user_entry,
        "profile":    request.user.profile,
    })