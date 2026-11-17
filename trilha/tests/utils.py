"""dados de apoio para os testes da trilha."""
from contas.models import Usuaria
from trilha.models import Desafio, Etapa


def criar_desafios(n_pre=3, n_trilha=2):
    pre = [
        Desafio.objects.create(
            etapa=Etapa.PRE_TRILHA,
            ordem=i,
            titulo=f"Tutorial {i}",
            descricao="Descrição",
            passos=[{"texto": f"Passo do tutorial {i}", "imagem": None}],
            dica=f"Dica do tutorial {i}",
        )
        for i in range(1, n_pre + 1)
    ]
    trilha = [
        Desafio.objects.create(
            etapa=Etapa.TRILHA,
            tipo=Desafio.Tipo.CONSTRUCAO,
            ordem=i,
            titulo=f"Construção {i}",
            descricao="Descrição",
        )
        for i in range(1, n_trilha + 1)
    ]
    return pre, trilha


def criar_aluna(email="aluna@exemplo.org", **campos):
    return Usuaria.objects.create_user(email, "senha-forte-123", first_name="Ana", **campos)


def criar_mentora(email="mentora@exemplo.org"):
    return Usuaria.objects.create_user(email, "senha-forte-123", perfil=Usuaria.Perfil.MENTORA)
