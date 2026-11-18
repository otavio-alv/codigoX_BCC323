from django.db import migrations

SIMULADORES = [
    ("atalhos", "Atalhos do teclado", 5),
    ("componentes", "Peças do computador", 5),
]


def criar_simuladores(apps, schema_editor):
    Simulador = apps.get_model("trilha", "Simulador")
    for tipo, titulo, pontos in SIMULADORES:
        Simulador.objects.get_or_create(
            tipo=tipo, defaults={"titulo": titulo, "pontos": pontos}
        )


def remover_simuladores(apps, schema_editor):
    Simulador = apps.get_model("trilha", "Simulador")
    Simulador.objects.filter(tipo__in=[tipo for tipo, _, _ in SIMULADORES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("trilha", "0002_simulador"),
    ]

    operations = [
        migrations.RunPython(criar_simuladores, remover_simuladores),
    ]
