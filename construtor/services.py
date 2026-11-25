"""regras do editor de telas.

formato da tela salva:
{"componentes": [
  {"id": "c1", "tipo": "rotulo", "props": {"texto": "ana", "cor_texto": "#1e1e24", "tamanho": "medio"}},
  {"id": "c2", "tipo": "arranjo_vertical", "props": {}, "filhos": [...]}
]}

a conferencia dos criterios existe tambem em static/js/construtor/criterios.js.
as duas precisam dar o mesmo resultado (ver construtor/tests/casos_criterios.json).
"""
from django.db import transaction

from trilha import services as trilha_services
from trilha.models import Desafio

from .models import TelaAluna

ARRANJOS = ("arranjo_horizontal", "arranjo_vertical")

# propriedades de cada tipo e o valor padrao delas
PADROES = {
    "rotulo": {"texto": "", "cor_texto": "#1E1E24", "tamanho": "medio"},
    "botao": {"texto": "Botão", "cor_fundo": "#0B7376", "cor_texto": "#FFFFFF", "tamanho": "medio"},
    "caixa_texto": {"dica": "", "senha": False},
    "imagem": {"imagem": ""},
    "arranjo_horizontal": {},
    "arranjo_vertical": {},
}

# as 6 cores da cartilha (nao ha seletor livre)
CORES = [
    ("#1E1E24", "Preto"),
    ("#FFFFFF", "Branco"),
    ("#0B7376", "Verde-água"),
    ("#C8402E", "Coral"),
    ("#FFD84D", "Amarelo"),
    ("#F4F4F2", "Cinza-claro"),
]
TAMANHOS = [("pequeno", "Pequeno"), ("medio", "Médio"), ("grande", "Grande")]
GALERIA = ["computador.svg", "coracao.svg", "estrela.svg", "flor.svg", "foguete.svg", "livro.svg"]

MAX_COMPONENTES = 40
MAX_TEXTO = 60


class TelaInvalida(Exception):
    """o json enviado nao tem o formato de uma tela."""


# ------------------------------------------------------------------ validacao


def _valida_props(tipo, props):
    if not isinstance(props, dict):
        raise TelaInvalida("As propriedades de um componente precisam ser um objeto.")
    padrao = PADROES[tipo]
    limpas = dict(padrao)
    cores = {c for c, _ in CORES}
    tamanhos = {t for t, _ in TAMANHOS}
    for chave, valor in props.items():
        if chave not in padrao:
            continue  # propriedade desconhecida e ignorada
        if chave in ("texto", "dica"):
            if not isinstance(valor, str) or len(valor) > MAX_TEXTO:
                raise TelaInvalida(f"O texto pode ter no máximo {MAX_TEXTO} letras.")
        elif chave in ("cor_fundo", "cor_texto"):
            if valor not in cores:
                raise TelaInvalida("Escolha uma das cores da cartilha.")
        elif chave == "tamanho":
            if valor not in tamanhos:
                raise TelaInvalida("Tamanho inválido.")
        elif chave == "senha":
            if not isinstance(valor, bool):
                raise TelaInvalida("A opção senha precisa ser verdadeiro ou falso.")
        elif chave == "imagem":
            if valor != "" and valor not in GALERIA:
                raise TelaInvalida("Escolha uma imagem da galeria.")
        limpas[chave] = valor
    return limpas


def _valida_componente(dados, dentro_de_arranjo, ids):
    if not isinstance(dados, dict):
        raise TelaInvalida("Componente inválido.")
    tipo = dados.get("tipo")
    if tipo not in PADROES:
        raise TelaInvalida("Tipo de componente desconhecido.")
    ident = dados.get("id")
    if not isinstance(ident, str) or not ident or len(ident) > 20 or ident in ids:
        raise TelaInvalida("Cada componente precisa de um id único.")
    ids.add(ident)
    componente = {"id": ident, "tipo": tipo, "props": _valida_props(tipo, dados.get("props", {}))}
    if tipo in ARRANJOS:
        if dentro_de_arranjo:
            raise TelaInvalida("Um arranjo não pode ficar dentro de outro arranjo.")
        filhos = dados.get("filhos", [])
        if not isinstance(filhos, list):
            raise TelaInvalida("Os filhos de um arranjo precisam ser uma lista.")
        componente["filhos"] = [_valida_componente(f, True, ids) for f in filhos]
    return componente


def normalizar_tela(dados):
    """confere o json da tela e devolve uma copia limpa, com as propriedades padrao preenchidas."""
    if not isinstance(dados, dict) or not isinstance(dados.get("componentes"), list):
        raise TelaInvalida("A tela precisa ter uma lista de componentes.")
    ids = set()
    componentes = [_valida_componente(c, False, ids) for c in dados["componentes"]]
    if len(ids) > MAX_COMPONENTES:
        raise TelaInvalida(f"A tela pode ter no máximo {MAX_COMPONENTES} componentes.")
    return {"componentes": componentes}


# ------------------------------------------------------------------ criterios


def _todos(componentes):
    """lista plana com os componentes e os filhos dos arranjos."""
    saida = []
    for c in componentes:
        saida.append(c)
        saida.extend(c.get("filhos") or [])
    return saida


def _normaliza_texto(valor):
    return " ".join(valor.split()).lower()


def _preenchido(valor):
    if isinstance(valor, str):
        return valor.strip() != ""
    return valor is not None and valor is not False


def _valor(componente, chave):
    props = componente.get("props") or {}
    if chave in props:
        return props[chave]
    return PADROES.get(componente.get("tipo"), {}).get(chave)


def _bate(valor, esperado):
    if esperado == "*":
        return _preenchido(valor)
    if isinstance(esperado, str):
        return isinstance(valor, str) and _normaliza_texto(valor) == _normaliza_texto(esperado)
    return type(valor) is type(esperado) and valor == esperado


def criterio_atendido(criterio, componentes):
    regra = criterio.get("regra")
    tipo = criterio.get("componente")
    candidatos = [c for c in _todos(componentes) if c.get("tipo") == tipo]
    if regra == "existe":
        esperadas = criterio.get("props") or {}
        return any(all(_bate(_valor(c, k), v) for k, v in esperadas.items()) for c in candidatos)
    if regra == "alterado":
        padrao = PADROES.get(tipo, {})
        chaves = criterio.get("props") or []
        return any(all(_valor(c, k) != padrao.get(k) for k in chaves) for c in candidatos)
    if regra == "minimo_filhos":
        n = criterio.get("n", 1)
        return any(len(c.get("filhos") or []) >= n for c in candidatos)
    return False


def conferir(criterios, tela):
    """devolve a lista de dicas dos criterios que falharam (vazia quando esta tudo certo)."""
    componentes = (tela or {}).get("componentes") or []
    return [c.get("dica", "") for c in criterios if not criterio_atendido(c, componentes)]


# ------------------------------------------------------------------ tela da aluna


def pode_editar(aluna, desafio):
    return desafio.tipo == Desafio.Tipo.CONSTRUCAO and trilha_services.desafio_liberado(aluna, desafio)


def obter_tela(aluna, desafio):
    tela = TelaAluna.objects.filter(aluna=aluna, desafio=desafio).first()
    return tela.componentes if tela else {"componentes": []}


def salvar_tela(aluna, desafio, dados):
    if not pode_editar(aluna, desafio):
        raise trilha_services.DesafioBloqueado("Este desafio ainda está trancado.")
    limpa = normalizar_tela(dados)
    tela, _ = TelaAluna.objects.update_or_create(
        aluna=aluna, desafio=desafio, defaults={"componentes": limpa}
    )
    return tela


def concluir_construcao(aluna, desafio, dados):
    """salva a tela, confere os criterios de novo no servidor e so entao conclui.

    devolve (dicas, pontos_ganhos); com dicas, nada e concluido.
    """
    with transaction.atomic():
        tela = salvar_tela(aluna, desafio, dados)
        dicas = conferir(desafio.criterios, tela.componentes)
        if dicas:
            return dicas, 0
        _, ganhos = trilha_services.concluir_desafio(aluna, desafio)
        return [], ganhos
