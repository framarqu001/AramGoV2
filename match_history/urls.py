from django.urls import path, include

from . import views

app_name = "match_history"

urlpatterns = [
    path("", views.home, name="home"),
    path("summoner/<str:game_name>-<str:tag>", views.details, name="details"),
    path("champions/",views.champions, name="champions"),
    path("summoner/", views.summoner, name="summoner"),  # Ensure this line exists
    path("update/", views.update, name="update"),
    path("about/", views.about, name="about"),
    
    # Authentication URLs
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    
    # Profile URLs
    path("profile/", views.profile, name="profile"),
    path("profile/settings/", views.profile_settings, name="profile_settings"),
    path("profile/connect-summoner/", views.connect_summoner, name="connect_summoner"),
    path("profile/disconnect-summoner/<str:summoner_puuid>/", views.disconnect_summoner, name="disconnect_summoner"),
    path("profile/set-primary-summoner/", views.set_primary_summoner, name="set_primary_summoner"),
]