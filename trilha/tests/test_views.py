from django.test import TestCase
from django.urls import reverse

from trilha import services

from .utils import criar_aluna, criar_desafios, criar_mentora

JSON = {"HTTP_ACCEPT": "application/json"}


class PainelViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()
        cls.mentora = criar_mentora()

    def test_deslogada_vai_para_o_login(self):
        resposta = self.client.get(reverse("trilha:painel"))
        self.assertRedirects(resposta, "/login/?next=/aluna/")

    def test_mentora_recebe_403(self):
        self.client.force_login(self.mentora)
        self.assertEqual(self.client.get(reverse("trilha:painel")).status_code, 403)

    def test_aluna_ve_o_painel(self):
        self.client.force_login(self.aluna)
        resposta = self.client.get(reverse("trilha:painel"))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "trilha/painel.html")
        self.assertContains(resposta, "Olá, Ana!")
        self.assertContains(resposta, "Tutorial 1")
        self.assertContains(resposta, "0 de 3 desafios concluídos")


class DesafioViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()

    def setUp(self):
        self.client.force_login(self.aluna)

    def test_desafio_liberado_mostra_passos_e_dica(self):
        resposta = self.client.get(reverse("trilha:desafio", args=[self.pre[0].pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Passo do tutorial 1")
        self.assertContains(resposta, "Dica do tutorial 1")
        self.assertContains(resposta, "Concluí o desafio")

    def test_desafio_trancado_volta_para_o_painel(self):
        resposta = self.client.get(reverse("trilha:desafio", args=[self.pre[1].pk]), follow=True)
        self.assertRedirects(resposta, reverse("trilha:painel"))
        self.assertContains(resposta, "ainda está trancado")

    def test_desafio_de_construcao_vai_para_o_editor(self):
        resposta = self.client.get(reverse("trilha:desafio", args=[self.trilha[0].pk]))
        self.assertRedirects(
            resposta, f"/aluna/construtor/{self.trilha[0].pk}/", fetch_redirect_response=False
        )

    def test_desafio_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("trilha:desafio", args=[9999])).status_code, 404)


class ConcluirViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()
        cls.mentora = criar_mentora()

    def url(self, desafio):
        return reverse("trilha:concluir", args=[desafio.pk])

    def test_concluir_responde_json_com_pontos(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(self.url(self.pre[0]), **JSON)
        self.assertEqual(resposta.status_code, 200)
        dados = resposta.json()
        self.assertTrue(dados["ok"])
        self.assertEqual(dados["pontos_ganhos"], 10)
        self.assertEqual(dados["total"], 10)
        self.assertEqual(dados["proximo"], reverse("trilha:desafio", args=[self.pre[1].pk]))

    def test_clique_duplo_pela_view(self):
        self.client.force_login(self.aluna)
        self.client.post(self.url(self.pre[0]), **JSON)
        dados = self.client.post(self.url(self.pre[0]), **JSON).json()
        self.assertEqual(dados["pontos_ganhos"], 0)
        self.assertEqual(services.total_pontos(self.aluna), 10)

    def test_concluir_trancado_da_400(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(self.url(self.pre[2]), **JSON)
        self.assertEqual(resposta.status_code, 400)
        self.assertFalse(resposta.json()["ok"])

    def test_concluir_sem_javascript_redireciona(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(self.url(self.pre[0]))
        self.assertRedirects(resposta, reverse("trilha:desafio", args=[self.pre[1].pk]))

    def test_desafio_de_construcao_nao_conclui_por_aqui(self):
        self.client.force_login(self.aluna)
        resposta = self.client.post(self.url(self.trilha[0]), **JSON)
        self.assertEqual(resposta.status_code, 400)

    def test_get_nao_e_permitido(self):
        self.client.force_login(self.aluna)
        self.assertEqual(self.client.get(self.url(self.pre[0])).status_code, 405)

    def test_mentora_recebe_403(self):
        self.client.force_login(self.mentora)
        self.assertEqual(self.client.post(self.url(self.pre[0]), **JSON).status_code, 403)
