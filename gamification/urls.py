# gamification/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("achievements/", views.achievements_view, name="achievements"),
    path("leaderboard/",  views.leaderboard_view,  name="leaderboard"),
]