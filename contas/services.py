import secrets

from django.shortcuts import get_object_or_404

from .models import Usuaria

PAGINA_INICIAL = {
    Usuaria.Perfil.ALUNA: "/aluna/",
    Usuaria.Perfil.MENTORA: "/mentora/",
    Usuaria.Perfil.ADMIN: "/admin/",
}

PALAVRAS_SENHA = [
    "sol", "lua", "mar", "flor", "rio", "vento", "pipa", "bola",
    "nuvem", "estrela", "ponte", "trem", "livro", "folha", "ilha", "gato",
]


def pagina_inicial(usuaria):
    """endereco para onde cada perfil vai depois do login."""
    return PAGINA_INICIAL.get(usuaria.perfil, "/admin/")


def gerar_senha():
    """senha facil de ditar e de digitar, como flor-lua-4821."""
    palavras = [secrets.choice(PALAVRAS_SENHA) for _ in range(2)]
    numero = f"{secrets.randbelow(10000):04d}"
    return "-".join(palavras + [numero])


def alunas_da_mentora(mentora):
    """alunas de todas as turmas em que a mentora esta vinculada como mentora."""
    return Usuaria.objects.filter(
        perfil=Usuaria.Perfil.ALUNA,
        vinculos__papel="aluna",
        vinculos__turma__vinculos__usuaria=mentora,
        vinculos__turma__vinculos__papel="mentora",
    ).distinct()


def redefinir_senha(mentora, aluna_id):
    """gera uma senha nova para a aluna. devolve (aluna, senha) e a senha nao fica guardada."""
    aluna = get_object_or_404(alunas_da_mentora(mentora), pk=aluna_id)
    senha = gerar_senha()
    aluna.set_password(senha)
    aluna.save(update_fields=["password"])
    return aluna, senha
