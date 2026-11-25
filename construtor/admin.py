from django.contrib import admin

from .models import TelaAluna


@admin.register(TelaAluna)
class TelaAlunaAdmin(admin.ModelAdmin):
    list_display = ("aluna", "desafio", "total_componentes", "atualizado_em")
    list_filter = ("desafio",)
    search_fields = ("aluna__email", "aluna__first_name")
    list_select_related = ("aluna", "desafio")
    readonly_fields = ("atualizado_em",)

    @admin.display(description="componentes")
    def total_componentes(self, tela):
        componentes = (tela.componentes or {}).get("componentes") or []
        return len(componentes) + sum(len(c.get("filhos") or []) for c in componentes)
