// simulador de atalhos: a aluna aperta cada atalho no teclado de verdade.
(function () {
  "use strict";

  var raiz = document.getElementById("simulador-atalhos");
  if (!raiz) return;

  // so atalhos que o navegador deixa a pagina capturar
  var ATALHOS = [
    { tecla: "c", acao: "Copiar", dica: "Ctrl + C", uso: "copia o que está selecionado." },
    { tecla: "v", acao: "Colar", dica: "Ctrl + V", uso: "cola o que você copiou." },
    { tecla: "x", acao: "Recortar", dica: "Ctrl + X", uso: "tira o texto do lugar para colar em outro." },
    { tecla: "z", acao: "Desfazer", dica: "Ctrl + Z", uso: "volta o último passo." },
    { tecla: "a", acao: "Selecionar tudo", dica: "Ctrl + A", uso: "seleciona o texto inteiro." },
    { tecla: "s", acao: "Salvar", dica: "Ctrl + S", uso: "salva o arquivo." },
  ];

  var atual = 0;
  var acao = document.getElementById("atalho-acao");
  var contador = document.getElementById("atalho-contador");
  var retorno = document.getElementById("atalho-retorno");
  var dica = document.getElementById("atalho-dica");
  var botaoDica = document.getElementById("botao-dica");
  var botaoConcluir = document.getElementById("botao-concluir-simulador");
  var resultado = document.getElementById("resultado-simulador");

  function mostrarAtalho() {
    var item = ATALHOS[atual];
    acao.textContent = item.acao;
    contador.textContent = "Atalho " + (atual + 1) + " de " + ATALHOS.length;
    dica.textContent = "";
    dica.hidden = true;
  }

  function terminar() {
    acao.textContent = "Você fez todos!";
    contador.textContent = ATALHOS.length + " de " + ATALHOS.length;
    retorno.textContent = "Muito bem! Agora clique em Concluí o simulador.";
    botaoDica.classList.add("hidden");
    botaoConcluir.disabled = false;
    botaoConcluir.focus();
  }

  document.addEventListener("keydown", function (evento) {
    if (atual >= ATALHOS.length) return;
    if (!(evento.ctrlKey || evento.metaKey)) return;
    var tecla = (evento.key || "").toLowerCase();
    if (tecla === "control" || tecla === "meta") return;

    var esperado = ATALHOS[atual];
    var conhecido = ATALHOS.some(function (a) { return a.tecla === tecla; });
    if (conhecido) evento.preventDefault();

    if (tecla === esperado.tecla) {
      retorno.textContent = "Acertou! " + esperado.dica + " " + esperado.uso;
      atual += 1;
      if (atual >= ATALHOS.length) terminar();
      else mostrarAtalho();
    } else {
      retorno.textContent = "Quase! Esse não é o atalho para " + esperado.acao + ". Tente de novo.";
    }
  });

  botaoDica.addEventListener("click", function () {
    dica.textContent = "Segure a tecla Ctrl e aperte: " + ATALHOS[atual].dica;
    dica.hidden = false;
  });

  botaoConcluir.addEventListener("click", async function () {
    botaoConcluir.disabled = true;
    var resposta = await window.CodigoX.enviarJSON(raiz.dataset.urlConcluir, {});
    var dados = resposta.dados || {};
    if (resposta.ok && dados.ok) {
      resultado.textContent = dados.mensagem + " Total: " + dados.total + " pontos.";
    } else {
      botaoConcluir.disabled = false;
      resultado.textContent = dados.erro || "Não deu certo agora. Tente de novo.";
    }
  });

  mostrarAtalho();
})();
