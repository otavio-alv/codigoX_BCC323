from django.test import TestCase
from django.urls import reverse

from inscricoes import services
from inscricoes.models import ALFABETO_PROTOCOLO, Candidatura


def dados_validos(**extra):
    dados = {
        "nome": "Joana Pereira",
        "idade": "19",
        "escola": "Escola Estadual Dom Pedro II",
        "cidade": "Ouro Preto",
        "carta": "Quero aprender a criar aplicativos.",
        "link_video": "",
        "nome_responsavel": "",
        "contato_responsavel": "",
    }
    dados.update(extra)
    return dados


class ProtocoloTests(TestCase):
    def test_protocolo_e_gerado_com_8_caracteres(self):
        candidatura = Candidatura.objects.create(
            nome="Joana", idade=19, escola="E", cidade="Ouro Preto", carta="Oi"
        )
        self.assertEqual(len(candidatura.protocolo), 8)
        self.assertTrue(all(c in ALFABETO_PROTOCOLO for c in candidatura.protocolo))

    def test_protocolos_diferentes(self):
        a = Candidatura.objects.create(nome="A", idade=19, escola="E", cidade="C", carta="Oi")
        b = Candidatura.objects.create(nome="B", idade=19, escola="E", cidade="C", carta="Oi")
        self.assertNotEqual(a.protocolo, b.protocolo)


class ConsentimentoTests(TestCase):
    """rn10: menor de idade precisa do consentimento da pessoa responsavel."""

    def test_maior_de_idade_nao_precisa(self):
        self.assertEqual(services.validar_consentimento(18, "", "", False), {})

    def test_menor_sem_nada_tem_tres_erros(self):
        erros = services.validar_consentimento(15, "", "", False)
        self.assertEqual(
            set(erros), {"nome_responsavel", "contato_responsavel", "consentimento"}
        )

    def test_menor_com_tudo_preenchido(self):
        self.assertEqual(
            services.validar_consentimento(15, "Maria", "(31) 99999-0000", True), {}
        )

    def test_espacos_nao_contam_como_preenchido(self):
        erros = services.validar_consentimento(15, "   ", "(31) 99999-0000", True)
        self.assertIn("nome_responsavel", erros)


class InscricaoViewTests(TestCase):
    url = reverse("inscricoes:inscricao")

    def test_formulario_abre_sem_login(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "inscricoes/formulario.html")

    def test_inscricao_de_maior_de_idade(self):
        resposta = self.client.post(self.url, dados_validos())
        candidatura = Candidatura.objects.get()
        self.assertEqual(candidatura.status, Candidatura.Status.PENDENTE)
        self.assertRedirects(
            resposta, f"{reverse('inscricoes:status')}?protocolo={candidatura.protocolo}"
        )

    def test_menor_sem_consentimento_nao_salva(self):
        resposta = self.client.post(self.url, dados_validos(idade="15"))
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(Candidatura.objects.exists())
        self.assertContains(resposta, "precisamos do nome da pessoa responsável")
        self.assertContains(resposta, 'role="alert"')

    def test_menor_com_consentimento_salva(self):
        self.client.post(
            self.url,
            dados_validos(
                idade="15",
                nome_responsavel="Maria Pereira",
                contato_responsavel="(31) 99999-0000",
                consentimento="on",
            ),
        )
        candidatura = Candidatura.objects.get()
        self.assertTrue(candidatura.consentimento)
        self.assertTrue(candidatura.menor_de_idade)

    def test_idade_fora_do_limite(self):
        self.client.post(self.url, dados_validos(idade="5"))
        self.assertFalse(Candidatura.objects.exists())

    def test_formulario_tem_csrf(self):
        self.assertContains(self.client.get(self.url), "csrfmiddlewaretoken")


class StatusViewTests(TestCase):
    url = reverse("inscricoes:status")

    @classmethod
    def setUpTestData(cls):
        cls.candidatura = Candidatura.objects.create(
            nome="Joana", idade=19, escola="E", cidade="C", carta="Oi"
        )

    def test_consulta_sem_protocolo(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertNotContains(resposta, "Não encontramos")

    def test_consulta_encontra_mesmo_em_minusculas(self):
        resposta = self.client.get(self.url, {"protocolo": self.candidatura.protocolo.lower()})
        self.assertContains(resposta, "está em avaliação")

    def test_protocolo_inexistente(self):
        resposta = self.client.get(self.url, {"protocolo": "ZZZZZZZZ"})
        self.assertContains(resposta, "Não encontramos esse protocolo")

    def test_status_aprovada(self):
        self.candidatura.status = Candidatura.Status.APROVADA
        self.candidatura.save()
        resposta = self.client.get(self.url, {"protocolo": self.candidatura.protocolo})
        self.assertContains(resposta, "você foi aprovada")
