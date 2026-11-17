"""decorators de acesso por perfil.

quem nao entrou vai para o login. quem entrou com outro perfil recebe a pagina 403.
"""
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Usuaria


def perfil_requerido(*perfis):
    def decorador(view):
        @wraps(view)
        def _view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.perfil not in perfis:
                raise PermissionDenied("Esta página não é para o seu perfil.")
            return view(request, *args, **kwargs)

        return _view

    return decorador


aluna_requerida = perfil_requerido(Usuaria.Perfil.ALUNA)
mentora_requerida = perfil_requerido(Usuaria.Perfil.MENTORA)
