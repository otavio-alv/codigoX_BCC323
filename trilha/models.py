from django.conf import settings
from django.db import models
from django.utils import timezone


class Etapa(models.TextChoices):
    PRE_TRILHA = "pre_trilha", "Pré-Trilha"
    TRILHA = "trilha", "Trilha"


class Desafio(models.Model):
    class Tipo(models.TextChoices):
        TUTORIAL = "tutorial", "Tutorial"
        CONSTRUCAO = "construcao", "Construção"

    etapa = models.CharField("etapa", max_length=20, choices=Etapa.choices)
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices, default=Tipo.TUTORIAL)
    ordem = models.PositiveSmallIntegerField("ordem")
    titulo = models.CharField("título", max_length=120)
    descricao = models.TextField("descrição")
    # lista de {"texto": "...", "imagem": "desafios/d01-1.png" ou null}
    passos = models.JSONField("passos", default=list, blank=True)
    dica = models.TextField("dica de ouro", blank=True)
    # so nos desafios de construcao (ver construtor/services.py)
    criterios = models.JSONField("critérios", default=list, blank=True)
    pontos = models.PositiveSmallIntegerField("pontos", default=10)

    class Meta:
        verbose_name = "desafio"
        verbose_name_plural = "desafios"
        ordering = ["etapa", "ordem"]
        constraints = [
            models.UniqueConstraint(fields=["etapa", "ordem"], name="desafio_ordem_unica_por_etapa"),
        ]

    def __str__(self):
        return f"{self.get_etapa_display()} {self.ordem}: {self.titulo}"


class Progresso(models.Model):
    """registro de que a aluna concluiu um desafio."""

    aluna = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progressos"
    )
    desafio = models.ForeignKey(
        Desafio, on_delete=models.CASCADE, null=True, blank=True, related_name="progressos"
    )
    concluido_em = models.DateTimeField("concluído em", default=timezone.now)

    class Meta:
        verbose_name = "progresso"
        verbose_name_plural = "progressos"
        ordering = ["-concluido_em"]
        constraints = [
            models.UniqueConstraint(fields=["aluna", "desafio"], name="progresso_desafio_unico"),
        ]

    def __str__(self):
        return f"{self.aluna} concluiu {self.desafio}"


class Pontuacao(models.Model):
    class Origem(models.TextChoices):
        DESAFIO = "desafio", "Desafio"
        SIMULADOR = "simulador", "Simulador"
        MENTORA = "mentora", "Mentora"

    aluna = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pontuacoes"
    )
    mentora = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pontuacoes_dadas",
    )
    valor = models.IntegerField("valor")
    motivo = models.CharField("motivo", max_length=200)
    origem = models.CharField("origem", max_length=20, choices=Origem.choices)
    criado_em = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        verbose_name = "pontuação"
        verbose_name_plural = "pontuações"
        ordering = ["-criado_em", "-id"]

    def __str__(self):
        return f"{self.valor:+d} para {self.aluna}: {self.motivo}"
