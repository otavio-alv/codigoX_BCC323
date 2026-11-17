from django.test import TestCase
from django.urls import reverse

from contas.models import Usuaria


class UsuariaTests(TestCase):
    def test_email_e_salvo_em_minusculas(self):
        usuaria = Usuaria.objects.create_user("Ana.Souza@Exemplo.org", "senha-forte-123")
        self.assertEqual(usuaria.email, "ana.souza@exemplo.org")

    def test_superusuaria_tem_perfil_admin(self):
        admin = Usuaria.objects.create_superuser("admin@exemplo.org", "senha-forte-123")
        self.assertEqual(admin.perfil, Usuaria.Perfil.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.eh_admin)

    def test_primeiro_nome(self):
        aluna = Usuaria(email="bia@exemplo.org", first_name="Beatriz Lima")
        self.assertEqual(aluna.primeiro_nome, "Beatriz")
        sem_nome = Usuaria(email="carla@exemplo.org")
        self.assertEqual(sem_nome.primeiro_nome, "carla")

    def test_helpers_de_perfil(self):
        aluna = Usuaria(email="a@exemplo.org", perfil=Usuaria.Perfil.ALUNA)
        mentora = Usuaria(email="m@exemplo.org", perfil=Usuaria.Perfil.MENTORA)
        self.assertTrue(aluna.eh_aluna)
        self.assertFalse(aluna.eh_mentora)
        self.assertTrue(mentora.eh_mentora)
        self.assertFalse(mentora.eh_admin)


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.aluna = Usuaria.objects.create_user(
            "aluna@exemplo.org", "senha-forte-123", first_name="Ana"
        )
        cls.mentora = Usuaria.objects.create_user(
            "mentora@exemplo.org", "senha-forte-123", perfil=Usuaria.Perfil.MENTORA
        )

    def test_tela_de_login_abre(self):
        resposta = self.client.get(reverse("contas:login"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "contas/login.html")
        self.assertContains(resposta, "Quero me inscrever")
        self.assertContains(resposta, "Esqueceu a senha?")

    def test_login_por_email_sem_diferenciar_maiusculas(self):
        resposta = self.client.post(
            reverse("contas:login"),
            {"username": "ALUNA@exemplo.org", "password": "senha-forte-123"},
        )
        self.assertRedirects(resposta, reverse("contas:inicio"), fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.aluna.pk)

    def test_senha_errada_mostra_mensagem(self):
        resposta = self.client.post(
            reverse("contas:login"),
            {"username": "aluna@exemplo.org", "password": "errada"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "E-mail ou senha não conferem")
        self.assertContains(resposta, 'role="alert"')
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_quem_ja_entrou_nao_ve_o_login_de_novo(self):
        self.client.force_login(self.aluna)
        resposta = self.client.get(reverse("contas:login"))
        self.assertEqual(resposta.status_code, 302)

    def test_logout_por_post(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(reverse("contas:logout"))
        self.assertRedirects(resposta, reverse("contas:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_por_get_nao_e_permitido(self):
        self.client.force_login(self.aluna)
        resposta = self.client.get(reverse("contas:logout"))
        self.assertEqual(resposta.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)


class RedirecionamentoPorPerfilTests(TestCase):
    def test_deslogada_vai_para_o_login(self):
        resposta = self.client.get("/")
        self.assertRedirects(resposta, reverse("contas:login"))

    def test_cada_perfil_vai_para_a_sua_pagina(self):
        casos = [
            (Usuaria.Perfil.ALUNA, "/aluna/"),
            (Usuaria.Perfil.MENTORA, "/mentora/"),
            (Usuaria.Perfil.ADMIN, "/admin/"),
        ]
        for perfil, destino in casos:
            with self.subTest(perfil=perfil):
                usuaria = Usuaria.objects.create_user(f"{perfil}@exemplo.org", "x", perfil=perfil)
                self.client.force_login(usuaria)
                resposta = self.client.get("/")
                self.assertRedirects(resposta, destino, fetch_redirect_response=False)
