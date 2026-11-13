from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import Usuaria


class UsuariaCriacaoForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuaria
        fields = ("email", "first_name", "last_name", "perfil")


class UsuariaAlteracaoForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuaria
        fields = "__all__"


@admin.register(Usuaria)
class UsuariaAdmin(UserAdmin):
    form = UsuariaAlteracaoForm
    add_form = UsuariaCriacaoForm

    list_display = ("email", "first_name", "last_name", "perfil", "is_active")
    list_filter = ("perfil", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("first_name", "email")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados pessoais", {"fields": ("first_name", "last_name", "perfil")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "perfil", "password1", "password2"),
            },
        ),
    )
