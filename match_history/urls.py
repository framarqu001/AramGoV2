from django.urls import path

from . import views

app_name = "match_history"

urlpatterns = [
    path("", views.home, name="home")
]