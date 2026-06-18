from django.urls import path 
from . import views  

urlpatterns = [
    # Tela inicial
    path("",              views.inicio_view,       name="inicio"),

    # Autenticação
    path("login/",        views.login_view,        name="login"),
    path("register/",     views.register_view,     name="register"),
    path("logout/",       views.logout_view,       name="logout"),

    # Páginas principais
    path("home/",         views.home_view,         name="home"),
    path("play/",         views.play_view,         name="play"),
    path("play/complete/", views.play_complete_view, name="play_complete"),
    path("profile/",      views.profile_view,      name="profile"),
    path("achievements/", views.achievements_view, name="achievements"),
    path("leaderboard/",  views.leaderboard_view,  name="leaderboard"),
    path("sobre/",        views.sobre_view,        name="sobre"),
]
