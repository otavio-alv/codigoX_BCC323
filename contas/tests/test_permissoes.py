from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contas.models import Usuaria
from contas.permissions import aluna_requerida, mentora_requerida
from gestao.models import Turma, TurmaUsuaria


@aluna_requerida
def view_da_aluna(request):
    return HttpResponse("ok")


@mentora_requerida
def view_da_mentora(request):
    return HttpResponse("ok")


class DecoratorsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.aluna = Usuaria.objects.create_user("aluna@exemplo.org", "x")
        cls.mentora = Usuaria.objects.create_user(
            "mentora@exemplo.org", "x", perfil=Usuaria.Perfil.MENTORA
        )

    def setUp(self):
        self.fabrica = RequestFactory()

    def pedido(self, usuaria):
        request = self.fabrica.get("/qualquer/")
        request.user = usuaria
        return request

    def test_deslogada_vai_para_o_login(self):
        resposta = view_da_aluna(self.pedido(AnonymousUser()))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn("/login/?next=/qualquer/", resposta.url)

    def test_perfil_certo_entra(self):
        self.assertEqual(view_da_aluna(self.pedido(self.aluna)).status_code, 200)
        self.assertEqual(view_da_mentora(self.pedido(self.mentora)).status_code, 200)

    def test_perfil_errado_e_negado(self):
        with self.assertRaises(PermissionDenied):
            view_da_aluna(self.pedido(self.mentora))
        with self.assertRaises(PermissionDenied):
            view_da_mentora(self.pedido(self.aluna))


class RedefinirSenhaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mentora = Usuaria.objects.create_user(
            "mentora@exemplo.org", "x", perfil=Usuaria.Perfil.MENTORA
        )
        cls.outra_mentora = Usuaria.objects.create_user(
            "outra@exemplo.org", "x", perfil=Usuaria.Perfil.MENTORA
        )
        cls.aluna = Usuaria.objects.create_user("aluna@exemplo.org", "antiga-123", first_name="Ana")
        turma = Turma.objects.create(nome="Turma A", ano=2026)
        TurmaUsuaria.objects.create(turma=turma, usuaria=cls.mentora, papel="mentora")
        TurmaUsuaria.objects.create(turma=turma, usuaria=cls.aluna, papel="aluna")
        cls.url = reverse("contas:redefinir_senha", args=[cls.aluna.pk])

    @mock.patch("contas.services.gerar_senha", return_value="sol-lua-1234")
    def test_mentora_da_turma_redefine_e_ve_a_senha(self, _):
        self.client.force_login(self.mentora)
        resposta = self.client.post(self.url, {"proxima": "/mentora/turmas/1/"}, follow=False)
        self.assertRedirects(resposta, "/mentora/turmas/1/", fetch_redirect_response=False)
        self.aluna.refresh_from_db()
        self.assertTrue(self.aluna.check_password("sol-lua-1234"))
        mensagens = [str(m) for m in resposta.wsgi_request._messages]
        self.assertTrue(any("sol-lua-1234" in m for m in mensagens))

    def test_mentora_de_outra_turma_nao_redefine(self):
        self.client.force_login(self.outra_mentora)
        resposta = self.client.post(self.url)
        self.assertEqual(resposta.status_code, 404)
        self.aluna.refresh_from_db()
        self.assertTrue(self.aluna.check_password("antiga-123"))

    def test_aluna_recebe_403(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(self.url)
        self.assertEqual(resposta.status_code, 403)
        self.assertTemplateUsed(resposta, "403.html")

    def test_get_nao_e_permitido(self):
        self.client.force_login(self.mentora)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_endereco_externo_em_proxima_e_ignorado(self):
        self.client.force_login(self.mentora)
        resposta = self.client.post(self.url, {"proxima": "https://site-estranho.com/"})
        self.assertRedirects(resposta, "/mentora/", fetch_redirect_response=False)

    def test_senha_gerada_e_facil_de_ditar(self):
        from contas.services import gerar_senha

        senha = gerar_senha()
        partes = senha.split("-")
        self.assertEqual(len(partes), 3)
        self.assertTrue(partes[2].isdigit())
