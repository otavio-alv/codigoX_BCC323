from django.contrib import admin

from .models import Desafio, Pontuacao, Progresso


@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ("ordem", "titulo", "etapa", "tipo", "pontos")
    list_display_links = ("titulo",)
    list_filter = ("etapa", "tipo")
    search_fields = ("titulo", "descricao")
    ordering = ("etapa", "ordem")


@admin.register(Progresso)
class ProgressoAdmin(admin.ModelAdmin):
    list_display = ("aluna", "desafio", "concluido_em")
    list_filter = ("desafio__etapa",)
    search_fields = ("aluna__email", "aluna__first_name")
    list_select_related = ("aluna", "desafio")
    date_hierarchy = "concluido_em"


@admin.register(Pontuacao)
class PontuacaoAdmin(admin.ModelAdmin):
    # pontos entram pelos services (conclusao e ajuste da mentora), por isso so leitura aqui
    list_display = ("aluna", "valor", "origem", "motivo", "mentora", "criado_em")
    list_filter = ("origem",)
    search_fields = ("aluna__email", "aluna__first_name", "motivo")
    list_select_related = ("aluna", "mentora")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
