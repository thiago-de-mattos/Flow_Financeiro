# gamification/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Badge, LeaderboardEntry, UserBadge
from .services.badges import award_eligible_badges
from .services.ranking import current_week_start, refresh_global_leaderboard

SCOPES = {"global", "friends", "school"}


@login_required
def achievements_view(request):
    award_eligible_badges(request.user)

    earned_ids = set(
        UserBadge.objects.filter(user=request.user).values_list("badge_id", flat=True)
    )
    return render(request, "achievements.html", {
        "badges": Badge.objects.order_by("id"),
        "earned_ids": earned_ids,
    })


@login_required
def leaderboard_view(request):
    scope = request.GET.get("scope", "global")
    if scope not in SCOPES:
        scope = "global"
    period = current_week_start()

    if scope == "global":
        refresh_global_leaderboard(period)

    entries = (
        LeaderboardEntry.objects.filter(scope=scope, period=period)
        .select_related("user")
        .order_by("rank")
    )
    user_entry = LeaderboardEntry.objects.filter(
        user=request.user, scope=scope, period=period
    ).first()

    return render(request, "leaderboard.html", {
        "entries":    entries,
        "scope":      scope,
        "user_entry": user_entry,
        "profile":    request.user.profile,
    })