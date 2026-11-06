# core/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("",          views.inicio_view,   name="inicio"),
    path("login/",    views.login_view,    name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/",   views.logout_view,   name="logout"),
    path("home/",     views.home_view,     name="home"),
    path("profile/",  views.profile_view,  name="profile"),
    path("sobre/",    views.sobre_view,    name="sobre"),
]