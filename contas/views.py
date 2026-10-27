from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .forms import LoginForm


class EntrarView(LoginView):
    template_name = "contas/login.html"
    authentication_form = LoginForm


@require_POST
def sair(request):
    logout(request)
    messages.info(request, "Você saiu da plataforma. Até a próxima!")
    return redirect("contas:login")


def inicio(request):
    """porta de entrada da plataforma: tudo comeca pela tela de login."""
    return redirect("contas:login")
