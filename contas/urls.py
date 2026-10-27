from django.urls import path

from . import views

app_name = "contas"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.EntrarView.as_view(), name="login"),
    path("logout/", views.sair, name="logout"),
]
