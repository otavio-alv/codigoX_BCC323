import threading

from django.db import connection
from django.test import TestCase, TransactionTestCase

from trilha import services
from trilha.models import Pontuacao, Progresso

from .utils import criar_aluna, criar_desafios


class LiberacaoTests(TestCase):
    """rn04: desafios liberados em ordem."""

    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()

    def test_primeiro_desafio_comeca_liberado(self):
        self.assertTrue(services.desafio_liberado(self.aluna, self.pre[0]))

    def test_segundo_so_abre_depois_do_primeiro(self):
        self.assertFalse(services.desafio_liberado(self.aluna, self.pre[1]))
        services.concluir_desafio(self.aluna, self.pre[0])
        self.assertTrue(services.desafio_liberado(self.aluna, self.pre[1]))

    def test_trilha_so_abre_depois_da_pre_trilha(self):
        self.assertFalse(services.desafio_liberado(self.aluna, self.trilha[0]))
        for desafio in self.pre:
            services.concluir_desafio(self.aluna, desafio)
        self.assertTrue(services.desafio_liberado(self.aluna, self.trilha[0]))
        self.assertFalse(services.desafio_liberado(self.aluna, self.trilha[1]))

    def test_concluir_desafio_trancado_nao_da_pontos(self):
        with self.assertRaises(services.DesafioBloqueado):
            services.concluir_desafio(self.aluna, self.pre[2])
        self.assertEqual(services.total_pontos(self.aluna), 0)
        self.assertFalse(Progresso.objects.exists())


class PontosTests(TestCase):
    """rn05: pontos entram uma unica vez."""

    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()

    def test_conclusao_vale_os_pontos_do_desafio(self):
        _, ganhos = services.concluir_desafio(self.aluna, self.pre[0])
        self.assertEqual(ganhos, 10)
        self.assertEqual(services.total_pontos(self.aluna), 10)
        pontuacao = Pontuacao.objects.get()
        self.assertEqual(pontuacao.origem, Pontuacao.Origem.DESAFIO)
        self.assertIn("Tutorial 1", pontuacao.motivo)

    def test_clique_duplo_nao_da_pontos_em_dobro(self):
        services.concluir_desafio(self.aluna, self.pre[0])
        _, ganhos = services.concluir_desafio(self.aluna, self.pre[0])
        self.assertEqual(ganhos, 0)
        self.assertEqual(services.total_pontos(self.aluna), 10)
        self.assertEqual(Progresso.objects.count(), 1)


class PainelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pre, cls.trilha = criar_desafios()
        cls.aluna = criar_aluna()

    def test_painel_inicial(self):
        dados = services.painel(self.aluna)
        self.assertEqual(dados["quadrados"], ["atual", "bloqueado", "bloqueado"])
        self.assertEqual(dados["desafio_atual"], self.pre[0])
        self.assertFalse(dados["pre_trilha_concluida"])
        self.assertEqual([i["estado"] for i in dados["trilha"]], ["bloqueado", "bloqueado"])

    def test_painel_depois_do_primeiro(self):
        services.concluir_desafio(self.aluna, self.pre[0])
        dados = services.painel(self.aluna)
        self.assertEqual(dados["quadrados"], ["feito", "atual", "bloqueado"])
        self.assertEqual(dados["feitos_pre"], 1)
        self.assertEqual(dados["pontos"], 10)

    def test_painel_com_pre_trilha_completa(self):
        for desafio in self.pre:
            services.concluir_desafio(self.aluna, desafio)
        dados = services.painel(self.aluna)
        self.assertTrue(dados["pre_trilha_concluida"])
        self.assertEqual(dados["desafio_atual"], self.trilha[0])
        self.assertEqual([i["estado"] for i in dados["trilha"]], ["atual", "bloqueado"])

    def test_proximo_desafio(self):
        self.assertEqual(services.proximo_desafio(self.pre[0]), self.pre[1])
        self.assertEqual(services.proximo_desafio(self.pre[-1]), self.trilha[0])
        self.assertIsNone(services.proximo_desafio(self.trilha[-1]))


class CliqueDuploSimultaneoTests(TransactionTestCase):
    """dois pedidos ao mesmo tempo, cada um na sua conexao com o banco."""

    def test_dois_cliques_ao_mesmo_tempo(self):
        pre, _ = criar_desafios(n_pre=1, n_trilha=0)
        aluna = criar_aluna()
        largada = threading.Barrier(2)
        ganhos = []

        def clicar():
            try:
                largada.wait()
                ganhos.append(services.concluir_desafio(aluna, pre[0])[1])
            finally:
                connection.close()

        threads = [threading.Thread(target=clicar) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(sorted(ganhos), [0, 10])
        self.assertEqual(services.total_pontos(aluna), 10)
