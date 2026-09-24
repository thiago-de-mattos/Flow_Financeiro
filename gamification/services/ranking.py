# gamification/services/ranking.py
import datetime

from django.utils import timezone

from core.models import Profile

from ..models import LeaderboardEntry


def current_week_start():
    hoje = timezone.localdate()
    return hoje - datetime.timedelta(days=hoje.weekday())


def refresh_global_leaderboard(period=None):
    period = period or current_week_start()
    profiles = Profile.objects.select_related("user").order_by("-coins", "user__created_at", "user__id")

    LeaderboardEntry.objects.filter(scope="global", period=period).delete()
    entries = [
        LeaderboardEntry(user=p.user, coins=p.coins, rank=i, scope="global", period=period)
        for i, p in enumerate(profiles, start=1)
    ]
    LeaderboardEntry.objects.bulk_create(entries)
    return entries