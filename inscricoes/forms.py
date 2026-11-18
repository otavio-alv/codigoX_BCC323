from django import forms

from . import services
from .models import Candidatura


class CandidaturaForm(forms.ModelForm):
    class Meta:
        model = Candidatura
        fields = [
            "nome",
            "idade",
            "escola",
            "cidade",
            "carta",
            "link_video",
            "nome_responsavel",
            "contato_responsavel",
            "consentimento",
        ]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "campo", "autocomplete": "name"}),
            "idade": forms.NumberInput(attrs={"class": "campo", "min": 8, "max": 30, "inputmode": "numeric"}),
            "escola": forms.TextInput(attrs={"class": "campo"}),
            "cidade": forms.TextInput(attrs={"class": "campo", "autocomplete": "address-level2"}),
            "carta": forms.Textarea(attrs={"class": "campo", "rows": 6}),
            "link_video": forms.URLInput(attrs={"class": "campo", "placeholder": "https://"}),
            "nome_responsavel": forms.TextInput(attrs={"class": "campo"}),
            "contato_responsavel": forms.TextInput(attrs={"class": "campo"}),
            "consentimento": forms.CheckboxInput(attrs={"class": "h-6 w-6 accent-codigo-agua-escuro"}),
        }
        help_texts = {
            "carta": "Conte por que você quer participar da jornada. Pode ser do seu jeito!",
            "link_video": "Opcional: um vídeo curtinho se apresentando (YouTube, Drive...).",
            "contato_responsavel": "Telefone com DDD ou e-mail.",
        }
        labels = {
            "consentimento": "A pessoa responsável autoriza a minha inscrição e o uso destes dados pela ONG Código X.",
        }

    def clean(self):
        dados = super().clean()
        erros = services.validar_consentimento(
            dados.get("idade"),
            dados.get("nome_responsavel"),
            dados.get("contato_responsavel"),
            dados.get("consentimento"),
        )
        for campo, mensagem in erros.items():
            self.add_error(campo, mensagem)
        return dados


class ConsultaProtocoloForm(forms.Form):
    protocolo = forms.CharField(
        label="Número do protocolo",
        max_length=8,
        min_length=8,
        widget=forms.TextInput(
            attrs={"class": "campo uppercase tracking-widest", "autocomplete": "off", "spellcheck": "false"}
        ),
    )

    def clean_protocolo(self):
        return self.cleaned_data["protocolo"].strip().upper()
