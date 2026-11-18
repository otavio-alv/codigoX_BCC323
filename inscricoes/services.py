"""regras de negocio das inscricoes."""
from .models import Candidatura

IDADE_ADULTA = 18


def validar_consentimento(idade, nome_responsavel, contato_responsavel, consentimento):
    """rn10: candidata menor de idade precisa dos dados e do consentimento da pessoa responsavel.

    devolve um dicionario campo -> mensagem; vazio quando esta tudo certo.
    """
    erros = {}
    if idade is None or idade >= IDADE_ADULTA:
        return erros
    if not (nome_responsavel or "").strip():
        erros["nome_responsavel"] = "Como você tem menos de 18 anos, precisamos do nome da pessoa responsável."
    if not (contato_responsavel or "").strip():
        erros["contato_responsavel"] = "Coloque um telefone ou e-mail da pessoa responsável."
    if not consentimento:
        erros["consentimento"] = "A pessoa responsável precisa autorizar a sua inscrição."
    return erros


def registrar_candidatura(form):
    """salva a candidatura de um formulario ja validado."""
    return form.save()


def buscar_por_protocolo(protocolo):
    protocolo = (protocolo or "").strip().upper()
    if not protocolo:
        return None
    return Candidatura.objects.filter(protocolo=protocolo).first()
