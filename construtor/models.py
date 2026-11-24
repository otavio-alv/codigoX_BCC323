from django.conf import settings
from django.db import models


def tela_vazia():
    return {"componentes": []}


class TelaAluna(models.Model):
    """tela montada pela aluna no editor, salva como json (formato em construtor/services.py)."""

    aluna = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telas"
    )
    desafio = models.ForeignKey(
        "trilha.Desafio", on_delete=models.CASCADE, related_name="telas"
    )
    componentes = models.JSONField("componentes", default=tela_vazia)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "tela da aluna"
        verbose_name_plural = "telas das alunas"
        ordering = ["-atualizado_em"]
        constraints = [
            models.UniqueConstraint(fields=["aluna", "desafio"], name="tela_aluna_desafio_unica"),
        ]

    def __str__(self):
        return f"Tela de {self.aluna} no desafio {self.desafio}"
