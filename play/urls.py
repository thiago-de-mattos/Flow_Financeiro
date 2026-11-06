# play/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("",          views.play_view,   name="play"),
    path("complete/", views.answer_view, name="play_complete"),
]