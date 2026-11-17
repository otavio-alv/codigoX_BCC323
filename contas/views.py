from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from . import services
from .forms import LoginForm
from .permissions import mentora_requerida


class EntrarView(LoginView):
    template_name = "contas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


@require_POST
def sair(request):
    logout(request)
    messages.info(request, "Você saiu da plataforma. Até a próxima!")
    return redirect("contas:login")


def inicio(request):
    """manda cada perfil para a sua pagina; quem nao entrou vai para o login."""
    if not request.user.is_authenticated:
        return redirect("contas:login")
    return redirect(services.pagina_inicial(request.user))


@require_POST
@mentora_requerida
def redefinir_senha_aluna(request, aluna_id):
    aluna, senha = services.redefinir_senha(request.user, aluna_id)
    messages.success(
        request,
        f"Nova senha de {aluna.get_full_name() or aluna.email}: {senha} . "
        "Anote e entregue para ela: esta senha não aparece de novo.",
    )
    proxima = request.POST.get("proxima", "")
    if not url_has_allowed_host_and_scheme(proxima, allowed_hosts={request.get_host()}):
        proxima = "/mentora/"
    return redirect(proxima)
