from django.urls import path

from . import views

app_name = "construtor"

urlpatterns = [
    path("aluna/construtor/<int:pk>/", views.editor, name="editor"),
    path("aluna/construtor/<int:pk>/salvar/", views.salvar, name="salvar"),
    path("aluna/construtor/<int:pk>/concluir/", views.concluir, name="concluir"),
]
