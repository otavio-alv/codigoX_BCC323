from django.urls import path

from . import views

app_name = "inscricoes"

urlpatterns = [
    path("inscricao/", views.inscricao, name="inscricao"),
    path("inscricao/status/", views.status, name="status"),
]
