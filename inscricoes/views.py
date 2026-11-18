from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from . import services
from .forms import CandidaturaForm, ConsultaProtocoloForm


def inscricao(request):
    form = CandidaturaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        candidatura = services.registrar_candidatura(form)
        messages.success(
            request,
            f"Inscrição enviada! O seu protocolo é {candidatura.protocolo}. Guarde esse número para consultar.",
        )
        return redirect(f"{reverse('inscricoes:status')}?protocolo={candidatura.protocolo}")
    return render(request, "inscricoes/formulario.html", {"form": form})


def status(request):
    form = ConsultaProtocoloForm(request.GET or None)
    candidatura = None
    procurou = False
    if form.is_bound and form.is_valid():
        procurou = True
        candidatura = services.buscar_por_protocolo(form.cleaned_data["protocolo"])
    return render(
        request,
        "inscricoes/status.html",
        {"form": form, "candidatura": candidatura, "procurou": procurou},
    )
