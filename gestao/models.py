from django.conf import settings
from django.db import models


class Turma(models.Model):
    class Etapa(models.TextChoices):
        MARATONA = "maratona", "Maratona"
        PRE_TRILHA = "pre_trilha", "Pré-Trilha"
        TRILHA = "trilha", "Trilha"

    nome = models.CharField("nome", max_length=100)
    etapa = models.CharField("etapa", max_length=20, choices=Etapa.choices, default=Etapa.PRE_TRILHA)
    ano = models.PositiveSmallIntegerField("ano")
    arquivada = models.BooleanField("arquivada", default=False)
    membros = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="TurmaUsuaria", related_name="turmas", blank=True
    )

    class Meta:
        verbose_name = "turma"
        verbose_name_plural = "turmas"
        ordering = ["-ano", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.ano})"


class TurmaUsuaria(models.Model):
    class Papel(models.TextChoices):
        ALUNA = "aluna", "Aluna"
        MENTORA = "mentora", "Mentora"

    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="vinculos")
    usuaria = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vinculos"
    )
    papel = models.CharField("papel", max_length=10, choices=Papel.choices, default=Papel.ALUNA)

    class Meta:
        verbose_name = "vínculo com turma"
        verbose_name_plural = "vínculos com turmas"
        constraints = [
            models.UniqueConstraint(fields=["turma", "usuaria"], name="turma_usuaria_unica"),
        ]

    def __str__(self):
        return f"{self.usuaria} em {self.turma} ({self.get_papel_display()})"
