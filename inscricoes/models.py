import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# sem letras e numeros que se confundem (o e 0, i e 1)
ALFABETO_PROTOCOLO = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def gerar_protocolo():
    return "".join(secrets.choice(ALFABETO_PROTOCOLO) for _ in range(8))


class Candidatura(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        APROVADA = "aprovada", "Aprovada"
        RECUSADA = "recusada", "Recusada"

    protocolo = models.CharField(
        "protocolo", max_length=8, unique=True, default=gerar_protocolo, editable=False
    )
    nome = models.CharField("nome completo", max_length=120)
    idade = models.PositiveSmallIntegerField(
        "idade", validators=[MinValueValidator(8), MaxValueValidator(30)]
    )
    escola = models.CharField("escola", max_length=120)
    cidade = models.CharField("cidade", max_length=80)
    carta = models.TextField("carta de motivação")
    link_video = models.URLField("link do vídeo", blank=True)

    # obrigatorios quando a candidata tem menos de 18 anos (rn10)
    nome_responsavel = models.CharField("nome da pessoa responsável", max_length=120, blank=True)
    contato_responsavel = models.CharField("contato da pessoa responsável", max_length=120, blank=True)
    consentimento = models.BooleanField("consentimento da pessoa responsável", default=False)

    status = models.CharField("status", max_length=10, choices=Status.choices, default=Status.PENDENTE)
    observacao = models.TextField("observação", blank=True)
    avaliada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidaturas_avaliadas",
    )
    # conta de aluna criada a partir desta candidatura (rn09); impede criar duas
    conta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidatura",
    )
    criado_em = models.DateTimeField("enviada em", auto_now_add=True)

    class Meta:
        verbose_name = "candidatura"
        verbose_name_plural = "candidaturas"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} ({self.protocolo})"

    @property
    def menor_de_idade(self):
        return self.idade is not None and self.idade < 18
