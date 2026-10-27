from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    """login com e-mail e senha, com mensagens simples."""

    username = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "E-mail ou senha não conferem. Confira e tente de novo.",
        "inactive": "Esta conta está desativada. Fale com a sua mentora.",
    }
