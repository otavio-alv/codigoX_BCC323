from django.contrib import admin
from django.db.models import Count

from .models import Turma, TurmaUsuaria


class TurmaUsuariaInline(admin.TabularInline):
    model = TurmaUsuaria
    extra = 1
    autocomplete_fields = ("usuaria",)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ("nome", "etapa", "ano", "arquivada", "total_membros")
    list_filter = ("etapa", "ano", "arquivada")
    search_fields = ("nome",)
    inlines = [TurmaUsuariaInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_total_membros=Count("vinculos"))

    @admin.display(description="membros", ordering="_total_membros")
    def total_membros(self, turma):
        return turma._total_membros


@admin.register(TurmaUsuaria)
class TurmaUsuariaAdmin(admin.ModelAdmin):
    list_display = ("usuaria", "turma", "papel")
    list_filter = ("papel", "turma")
    search_fields = ("usuaria__email", "usuaria__first_name", "turma__nome")
    autocomplete_fields = ("usuaria", "turma")
    list_select_related = ("usuaria", "turma")
