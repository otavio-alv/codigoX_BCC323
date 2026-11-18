"""regras de negocio da trilha: liberacao em ordem (rn04), pontos (rn05) e medalhas."""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum

from .models import Desafio, Etapa, Pontuacao, Progresso, Simulador

FEITO = "feito"
ATUAL = "atual"
BLOQUEADO = "bloqueado"


class DesafioBloqueado(Exception):
    """a aluna tentou concluir um desafio que ainda nao foi liberado."""


def total_pontos(aluna):
    return aluna.pontuacoes.aggregate(total=Sum("valor"))["total"] or 0


def ids_concluidos(aluna):
    return set(
        Progresso.objects.filter(aluna=aluna, desafio__isnull=False).values_list(
            "desafio_id", flat=True
        )
    )


def pre_trilha_concluida(aluna):
    total = Desafio.objects.filter(etapa=Etapa.PRE_TRILHA).count()
    feitos = Progresso.objects.filter(aluna=aluna, desafio__etapa=Etapa.PRE_TRILHA).count()
    return total > 0 and feitos >= total


def desafio_liberado(aluna, desafio):
    """rn04: o desafio n so abre depois do n-1; a trilha so abre depois da pre-trilha."""
    if desafio.etapa == Etapa.TRILHA and not pre_trilha_concluida(aluna):
        return False
    anterior = (
        Desafio.objects.filter(etapa=desafio.etapa, ordem__lt=desafio.ordem)
        .order_by("-ordem")
        .first()
    )
    return anterior is None or Progresso.objects.filter(aluna=aluna, desafio=anterior).exists()


def _situacao(desafios, concluidos, etapa_aberta):
    """marca cada desafio como feito, atual (liberado) ou bloqueado, seguindo a rn04."""
    itens = []
    anterior_feito = etapa_aberta
    for desafio in desafios:
        if desafio.id in concluidos:
            estado = FEITO
        elif anterior_feito:
            estado = ATUAL
        else:
            estado = BLOQUEADO
        itens.append({"desafio": desafio, "estado": estado})
        anterior_feito = etapa_aberta and desafio.id in concluidos
    return itens


def painel(aluna):
    """dados da pagina minha trilha, com poucas consultas ao banco."""
    concluidos = ids_concluidos(aluna)
    desafios = list(Desafio.objects.all())
    pre = [d for d in desafios if d.etapa == Etapa.PRE_TRILHA]
    trilha = [d for d in desafios if d.etapa == Etapa.TRILHA]

    pre_ok = bool(pre) and all(d.id in concluidos for d in pre)
    itens_pre = _situacao(pre, concluidos, etapa_aberta=True)
    itens_trilha = _situacao(trilha, concluidos, etapa_aberta=pre_ok)
    atual = next((i["desafio"] for i in itens_pre + itens_trilha if i["estado"] == ATUAL), None)

    return {
        "pre_trilha": itens_pre,
        "trilha": itens_trilha,
        "pre_trilha_concluida": pre_ok,
        "quadrados": [i["estado"] for i in itens_pre],
        "feitos_pre": sum(1 for i in itens_pre if i["estado"] == FEITO),
        "total_pre": len(itens_pre),
        "feitos_trilha": sum(1 for i in itens_trilha if i["estado"] == FEITO),
        "total_trilha": len(itens_trilha),
        "desafio_atual": atual,
        "pontos": total_pontos(aluna),
    }


def proximo_desafio(desafio):
    """proximo desafio da mesma etapa; no fim da pre-trilha, o primeiro da trilha."""
    seguinte = (
        Desafio.objects.filter(etapa=desafio.etapa, ordem__gt=desafio.ordem).order_by("ordem").first()
    )
    if seguinte is None and desafio.etapa == Etapa.PRE_TRILHA:
        seguinte = Desafio.objects.filter(etapa=Etapa.TRILHA).order_by("ordem").first()
    return seguinte


def concluir_desafio(aluna, desafio):
    """rn05: registra a conclusao e da os pontos uma unica vez.

    trava a linha da aluna para que dois cliques ao mesmo tempo sejam atendidos
    um depois do outro; o segundo encontra o progresso ja criado e nao ganha pontos.
    devolve (progresso, pontos_ganhos).
    """
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=aluna.pk)
        if not desafio_liberado(aluna, desafio):
            raise DesafioBloqueado("Este desafio ainda está trancado.")
        progresso, criado = Progresso.objects.get_or_create(aluna=aluna, desafio=desafio)
        if not criado:
            return progresso, 0
        Pontuacao.objects.create(
            aluna=aluna,
            valor=desafio.pontos,
            motivo=f"Desafio concluído: {desafio.titulo}",
            origem=Pontuacao.Origem.DESAFIO,
        )
        return progresso, desafio.pontos


def simulador_concluido(aluna, simulador):
    return Progresso.objects.filter(aluna=aluna, simulador=simulador).exists()


def concluir_simulador(aluna, simulador):
    """rn05 para simuladores: vale simulador.pontos uma unica vez. devolve (progresso, pontos_ganhos)."""
    with transaction.atomic():
        get_user_model().objects.select_for_update().get(pk=aluna.pk)
        progresso, criado = Progresso.objects.get_or_create(aluna=aluna, simulador=simulador)
        if not criado:
            return progresso, 0
        Pontuacao.objects.create(
            aluna=aluna,
            valor=simulador.pontos,
            motivo=f"Simulador concluído: {simulador.titulo}",
            origem=Pontuacao.Origem.SIMULADOR,
        )
        return progresso, simulador.pontos


def medalhas(aluna):
    """medalhas calculadas a partir do progresso, sem tabela propria."""
    concluidos = ids_concluidos(aluna)
    pre = dict(Desafio.objects.filter(etapa=Etapa.PRE_TRILHA).values_list("ordem", "id"))
    construcao = list(
        Desafio.objects.filter(tipo=Desafio.Tipo.CONSTRUCAO).values_list("id", flat=True)
    )
    simuladores = set(
        Progresso.objects.filter(aluna=aluna, simulador__isnull=False).values_list(
            "simulador__tipo", flat=True
        )
    )

    primeiros_cinco = [pre.get(ordem) for ordem in range(1, 6)]
    return [
        {
            "nome": "Exploradora",
            "descricao": "Concluiu os desafios 1 a 5 da Pré-Trilha.",
            "icone": "busca",
            "conquistada": all(i is not None and i in concluidos for i in primeiros_cinco),
        },
        {
            "nome": "Conectada",
            "descricao": "Concluiu os 13 desafios da Pré-Trilha.",
            "icone": "computador",
            "conquistada": bool(pre) and all(i in concluidos for i in pre.values()),
        },
        {
            "nome": "Mestre dos atalhos",
            "descricao": "Concluiu o simulador de atalhos do teclado.",
            "icone": "teclado",
            "conquistada": Simulador.Tipo.ATALHOS in simuladores,
        },
        {
            "nome": "Criadora de telas",
            "descricao": "Concluiu o primeiro desafio de construção.",
            "icone": "celular",
            "conquistada": any(i in concluidos for i in construcao),
        },
        {
            "nome": "Inventora",
            "descricao": "Concluiu os 7 desafios de construção.",
            "icone": "estrela",
            "conquistada": bool(construcao) and all(i in concluidos for i in construcao),
        },
    ]


def perfil(aluna):
    """dados da pagina meu perfil: pontos, historico e medalhas."""
    lista_medalhas = medalhas(aluna)
    return {
        "pontos": total_pontos(aluna),
        "medalhas": lista_medalhas,
        "total_medalhas": sum(1 for m in lista_medalhas if m["conquistada"]),
        "historico": aluna.pontuacoes.select_related("mentora")[:50],
        "desafios_concluidos": Progresso.objects.filter(aluna=aluna, desafio__isnull=False).count(),
    }
