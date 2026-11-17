from django.urls import path

from . import views

app_name = "trilha"

urlpatterns = [
    path("aluna/", views.painel, name="painel"),
    path("aluna/desafio/<int:pk>/", views.desafio, name="desafio"),
    path("aluna/desafio/<int:pk>/concluir/", views.concluir, name="concluir"),
]
