from django.urls import path, include

from . import views

app_name = "match_history"

urlpatterns = [
    path("", views.home, name="home"),
    path("summoner/<str:game_name>-<str:tag>", views.details, name="details"),
    path("champions/",views.champions, name="champions"),
    path("summoner/", views.summoner, name="summoner"),  # Ensure this line exists
    path("update/", views.update, name="update"),

]