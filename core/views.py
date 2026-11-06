# core/views.py
from datetime import date

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from gamification.models import UserBadge
from gamification.services.badges import award_eligible_badges
from play.models import LessonProgress

from .forms import LoginForm, RegisterForm

AVATARES = ["pessoa1", "pessoa2", "pessoa3", "pessoa4", "pessoa5", "pessoa6"]


def inicio_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "inicio.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()          # o signal cria o Profile
        login(request, user)
        return redirect("home")

    return render(request, "register.html", {
        "form": form,
        "today": date.today().strftime("%Y-%m-%d"),
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request.POST or None, request=request)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("home")

    return render(request, "login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("inicio")


@login_required
def home_view(request):
    profile = request.user.profile
    profile.update_streak()
    award_eligible_badges(request.user, profile)
    return render(request, "home.html", {"profile": profile})


@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        avatar = request.POST.get("avatar")
        if avatar in AVATARES:
            profile.avatar = avatar
            profile.save(update_fields=["avatar"])
        return redirect("profile")

    award_eligible_badges(request.user, profile)

    return render(request, "profile.html", {
        "profile":      profile,
        "badges":       UserBadge.objects.filter(user=request.user).select_related("badge"),
        "lessons_done": LessonProgress.objects.filter(user=request.user, completed=True).count(),
        "avatares":     AVATARES,
    })


@login_required
def sobre_view(request):
    return render(request, "sobre.html")