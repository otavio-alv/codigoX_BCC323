import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_POST

from contas.permissions import aluna_requerida
from trilha import services as trilha_services
from trilha.models import Desafio, Progresso

from . import services


def _desafio(pk):
    return get_object_or_404(Desafio, pk=pk, tipo=Desafio.Tipo.CONSTRUCAO)


def _ler_json(request):
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@aluna_requerida
def editor(request, pk):
    desafio = _desafio(pk)
    if not services.pode_editar(request.user, desafio):
        messages.warning(request, "Esse desafio ainda está trancado. Termine o anterior primeiro!")
        return redirect("trilha:painel")

    proximo = trilha_services.proximo_desafio(desafio)
    dados_editor = {
        "tela": services.obter_tela(request.user, desafio),
        "criterios": desafio.criterios,
        "padroes": services.PADROES,
        "cores": [{"valor": v, "nome": n} for v, n in services.CORES],
        "tamanhos": [{"valor": v, "nome": n} for v, n in services.TAMANHOS],
        "galeria": [{"nome": n, "url": static(f"img/galeria/{n}")} for n in services.GALERIA],
        "urls": {
            "salvar": reverse("construtor:salvar", args=[desafio.pk]),
            "concluir": reverse("construtor:concluir", args=[desafio.pk]),
            "painel": reverse("trilha:painel"),
            "proximo": f"/aluna/construtor/{proximo.pk}/" if proximo else None,
        },
    }
    contexto = {
        "desafio": desafio,
        "concluido": Progresso.objects.filter(aluna=request.user, desafio=desafio).exists(),
        "dados_editor": dados_editor,
    }
    return render(request, "construtor/editor.html", contexto)


@require_POST
@aluna_requerida
def salvar(request, pk):
    desafio = _desafio(pk)
    dados = _ler_json(request)
    if dados is None:
        return JsonResponse({"ok": False, "erro": "Não entendi a tela enviada."}, status=400)
    try:
        tela = services.salvar_tela(request.user, desafio, dados)
    except (services.TelaInvalida, trilha_services.DesafioBloqueado) as erro:
        return JsonResponse({"ok": False, "erro": str(erro)}, status=400)
    return JsonResponse({"ok": True, "salvo_em": tela.atualizado_em.isoformat()})


@require_POST
@aluna_requerida
def concluir(request, pk):
    desafio = _desafio(pk)
    dados = _ler_json(request)
    if dados is None:
        return JsonResponse({"ok": False, "erro": "Não entendi a tela enviada."}, status=400)
    try:
        dicas, ganhos = services.concluir_construcao(request.user, desafio, dados)
    except (services.TelaInvalida, trilha_services.DesafioBloqueado) as erro:
        return JsonResponse({"ok": False, "erro": str(erro), "dicas": []}, status=400)
    if dicas:
        return JsonResponse({"ok": False, "dicas": dicas}, status=400)

    proximo = trilha_services.proximo_desafio(desafio)
    mensagem = (
        f"Tela pronta! Você ganhou {ganhos} pontos." if ganhos else "Tela salva. Você já tinha concluído este desafio."
    )
    return JsonResponse(
        {
            "ok": True,
            "pontos_ganhos": ganhos,
            "total": trilha_services.total_pontos(request.user),
            "proximo": f"/aluna/construtor/{proximo.pk}/" if proximo else None,
            "mensagem": mensagem,
        }
    )
