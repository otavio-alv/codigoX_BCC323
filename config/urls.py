from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Jornada Código X"
admin.site.site_title = "Jornada Código X"
admin.site.index_title = "Administração da plataforma"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contas.urls")),
]
