from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from trilha import services
from trilha.models import Desafio, Etapa, Pontuacao, Progresso, Simulador

from .utils import criar_aluna, criar_desafios, criar_mentora

JSON = {"HTTP_ACCEPT": "application/json"}


class SimuladorServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Simulador.objects.all().delete()
        cls.atalhos = Simulador.objects.create(tipo="atalhos", titulo="Atalhos")
        cls.aluna = criar_aluna()

    def test_simulador_vale_5_pontos_uma_vez(self):
        _, ganhos = services.concluir_simulador(self.aluna, self.atalhos)
        self.assertEqual(ganhos, 5)
        _, ganhos = services.concluir_simulador(self.aluna, self.atalhos)
        self.assertEqual(ganhos, 0)
        self.assertEqual(services.total_pontos(self.aluna), 5)
        self.assertEqual(Pontuacao.objects.get().origem, Pontuacao.Origem.SIMULADOR)

    def test_progresso_nao_aceita_desafio_e_simulador_juntos(self):
        desafio = Desafio.objects.create(etapa=Etapa.PRE_TRILHA, ordem=1, titulo="T", descricao="D")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Progresso.objects.create(aluna=self.aluna, desafio=desafio, simulador=self.atalhos)

    def test_progresso_nao_aceita_nenhum_dos_dois(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Progresso.objects.create(aluna=self.aluna)


class MedalhasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Simulador.objects.all().delete()
        cls.pre, cls.trilha = criar_desafios(n_pre=6, n_trilha=2)
        cls.atalhos = Simulador.objects.create(tipo="atalhos", titulo="Atalhos")
        cls.aluna = criar_aluna()

    def conquistadas(self):
        return {m["nome"] for m in services.medalhas(self.aluna) if m["conquistada"]}

    def test_sem_progresso_nenhuma_medalha(self):
        self.assertEqual(self.conquistadas(), set())

    def test_exploradora_com_os_cinco_primeiros(self):
        for desafio in self.pre[:5]:
            services.concluir_desafio(self.aluna, desafio)
        self.assertEqual(self.conquistadas(), {"Exploradora"})

    def test_conectada_criadora_e_inventora(self):
        for desafio in self.pre:
            services.concluir_desafio(self.aluna, desafio)
        self.assertIn("Conectada", self.conquistadas())
        services.concluir_desafio(self.aluna, self.trilha[0])
        self.assertIn("Criadora de telas", self.conquistadas())
        self.assertNotIn("Inventora", self.conquistadas())
        services.concluir_desafio(self.aluna, self.trilha[1])
        self.assertIn("Inventora", self.conquistadas())

    def test_mestre_dos_atalhos(self):
        services.concluir_simulador(self.aluna, self.atalhos)
        self.assertEqual(self.conquistadas(), {"Mestre dos atalhos"})


class SimuladorViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Simulador.objects.all().delete()
        Simulador.objects.create(tipo="atalhos", titulo="Treino de atalhos")
        Simulador.objects.create(tipo="componentes", titulo="Quiz dos componentes")
        cls.aluna = criar_aluna()
        cls.mentora = criar_mentora()

    def test_telas_dos_dois_simuladores(self):
        self.client.force_login(self.aluna)
        for tipo, template in [
            ("atalhos", "trilha/simulador_atalhos.html"),
            ("componentes", "trilha/simulador_componentes.html"),
        ]:
            with self.subTest(tipo=tipo):
                resposta = self.client.get(reverse("trilha:simulador", args=[tipo]))
                self.assertEqual(resposta.status_code, 200)
                self.assertTemplateUsed(resposta, template)

    def test_tipo_inexistente_da_404(self):
        self.client.force_login(self.aluna)
        self.assertEqual(self.client.get(reverse("trilha:simulador", args=["meet"])).status_code, 404)

    def test_concluir_por_json(self):
        self.client.force_login(self.aluna)
        url = reverse("trilha:concluir_simulador", args=["atalhos"])
        dados = self.client.post(url, **JSON).json()
        self.assertEqual(dados["pontos_ganhos"], 5)
        dados = self.client.post(url, **JSON).json()
        self.assertEqual(dados["pontos_ganhos"], 0)
        self.assertEqual(dados["total"], 5)

    def test_mentora_nao_conclui_simulador(self):
        self.client.force_login(self.mentora)
        url = reverse("trilha:concluir_simulador", args=["atalhos"])
        self.assertEqual(self.client.post(url, **JSON).status_code, 403)

    def test_concluir_por_get_nao_e_permitido(self):
        self.client.force_login(self.aluna)
        url = reverse("trilha:concluir_simulador", args=["atalhos"])
        self.assertEqual(self.client.get(url).status_code, 405)


class PerfilViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pre, _ = criar_desafios()
        cls.aluna = criar_aluna()

    def test_perfil_mostra_pontos_medalhas_e_historico(self):
        services.concluir_desafio(self.aluna, self.pre[0])
        self.client.force_login(self.aluna)
        resposta = self.client.get(reverse("trilha:perfil"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context["pontos"], 10)
        self.assertContains(resposta, "Exploradora")
        self.assertContains(resposta, "Desafio concluído: Tutorial 1")

    def test_perfil_exige_login(self):
        resposta = self.client.get(reverse("trilha:perfil"))
        self.assertEqual(resposta.status_code, 302)
