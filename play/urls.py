from django.urls import path

from . import views


urlpatterns = [
    path("", views.play_view, name="play"),
    path("fase/<int:fase_id>/", views.fase_view, name="fase"),
    path("complete/", views.answer_view, name="play_complete"),
]