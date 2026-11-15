from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from contas.permissions import aluna_requerida

from . import services
from .models import Desafio, Progresso


def _quer_json(request):
    return "application/json" in request.headers.get("Accept", "")


@aluna_requerida
def painel(request):
    return render(request, "trilha/painel.html", services.painel(request.user))


@aluna_requerida
def desafio(request, pk):
    desafio = get_object_or_404(Desafio, pk=pk)
    if desafio.tipo == Desafio.Tipo.CONSTRUCAO:
        return redirect(f"/aluna/construtor/{desafio.pk}/")
    if not services.desafio_liberado(request.user, desafio):
        messages.warning(request, "Esse desafio ainda está trancado. Termine o anterior primeiro!")
        return redirect("trilha:painel")
    contexto = {
        "desafio": desafio,
        "concluido": Progresso.objects.filter(aluna=request.user, desafio=desafio).exists(),
        "proximo": services.proximo_desafio(desafio),
    }
    return render(request, "trilha/desafio_tutorial.html", contexto)


@require_POST
@aluna_requerida
def concluir(request, pk):
    desafio = get_object_or_404(Desafio, pk=pk)
    if desafio.tipo != Desafio.Tipo.TUTORIAL:
        erro = "Este desafio é concluído no editor de telas."
        if _quer_json(request):
            return JsonResponse({"ok": False, "erro": erro}, status=400)
        messages.warning(request, erro)
        return redirect("trilha:painel")

    try:
        _, ganhos = services.concluir_desafio(request.user, desafio)
    except services.DesafioBloqueado as erro:
        if _quer_json(request):
            return JsonResponse({"ok": False, "erro": str(erro)}, status=400)
        messages.warning(request, str(erro))
        return redirect("trilha:painel")

    proximo = services.proximo_desafio(desafio)
    url_proximo = reverse("trilha:desafio", args=[proximo.pk]) if proximo else None
    mensagem = (
        f"Muito bem! Você ganhou {ganhos} pontos." if ganhos else "Você já tinha concluído este desafio."
    )
    if _quer_json(request):
        return JsonResponse(
            {
                "ok": True,
                "pontos_ganhos": ganhos,
                "total": services.total_pontos(request.user),
                "proximo": url_proximo,
                "mensagem": mensagem,
            }
        )
    messages.success(request, mensagem)
    return redirect(url_proximo or reverse("trilha:painel"))
