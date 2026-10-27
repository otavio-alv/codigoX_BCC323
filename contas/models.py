from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuariaManager(BaseUserManager):
    """cria usuarias usando o e-mail no lugar do nome de usuario."""

    use_in_migrations = True

    def _criar(self, email, password, **campos):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuaria = self.model(email=self.normalize_email(email).lower(), **campos)
        usuaria.set_password(password)
        usuaria.save(using=self._db)
        return usuaria

    def create_user(self, email, password=None, **campos):
        campos.setdefault("is_staff", False)
        campos.setdefault("is_superuser", False)
        return self._criar(email, password, **campos)

    def create_superuser(self, email, password=None, **campos):
        campos.setdefault("perfil", Usuaria.Perfil.ADMIN)
        campos.setdefault("is_staff", True)
        campos.setdefault("is_superuser", True)
        return self._criar(email, password, **campos)

    def get_by_natural_key(self, email):
        # login sem diferenciar maiusculas de minusculas no e-mail.
        return self.get(email__iexact=email)


class Usuaria(AbstractUser):
    class Perfil(models.TextChoices):
        ALUNA = "aluna", "Aluna"
        MENTORA = "mentora", "Mentora"
        ADMIN = "admin", "Administração"

    username = None
    email = models.EmailField("e-mail", unique=True)
    perfil = models.CharField(
        "perfil", max_length=10, choices=Perfil.choices, default=Perfil.ALUNA
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuariaManager()

    class Meta:
        verbose_name = "usuária"
        verbose_name_plural = "usuárias"
        ordering = ["first_name", "email"]

    def __str__(self):
        return self.get_full_name() or self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        if self.perfil == self.Perfil.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def eh_aluna(self):
        return self.perfil == self.Perfil.ALUNA

    @property
    def eh_mentora(self):
        return self.perfil == self.Perfil.MENTORA

    @property
    def eh_admin(self):
        return self.perfil == self.Perfil.ADMIN or self.is_superuser

    @property
    def primeiro_nome(self):
        """nome mostrado em telas vistas por outras alunas."""
        if self.first_name.strip():
            return self.first_name.split()[0]
        return self.email.split("@")[0]
