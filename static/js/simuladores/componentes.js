// quiz dos componentes do computador: uma pergunta por vez, refaz ate acertar.
(function () {
  "use strict";

  var raiz = document.getElementById("simulador-componentes");
  if (!raiz) return;

  var PERGUNTAS = [
    {
      texto: "Qual peça mostra as imagens e os textos para você ver?",
      opcoes: ["Monitor", "Teclado", "Mouse", "Caixa de som"],
      certa: 0,
      explicacao: "O monitor é a tela do computador.",
    },
    {
      texto: "Com qual peça você digita letras e números?",
      opcoes: ["Webcam", "Teclado", "Monitor", "Processador"],
      certa: 1,
      explicacao: "O teclado tem uma tecla para cada letra, número e sinal.",
    },
    {
      texto: "Qual peça move a setinha na tela e clica nas coisas?",
      opcoes: ["Caixa de som", "Memória RAM", "Mouse (ou touchpad do notebook)", "Webcam"],
      certa: 2,
      explicacao: "No notebook, o touchpad faz o papel do mouse.",
    },
    {
      texto: "Qual peça é o cérebro do computador e faz todas as contas?",
      opcoes: ["Processador", "Monitor", "Teclado", "Fone de ouvido"],
      certa: 0,
      explicacao: "O processador executa as instruções dos programas.",
    },
    {
      texto: "Onde os arquivos ficam guardados mesmo com o computador desligado?",
      opcoes: ["Memória RAM", "Mouse", "Armazenamento (HD ou SSD)", "Monitor"],
      certa: 2,
      explicacao: "O HD ou SSD guarda fotos, textos e programas para sempre (até você apagar).",
    },
    {
      texto: "O que guarda o que está aberto agora e se apaga quando o computador desliga?",
      opcoes: ["Armazenamento (HD ou SSD)", "Memória RAM", "Webcam", "Teclado"],
      certa: 1,
      explicacao: "A memória RAM é rápida, mas esquece tudo quando a energia acaba.",
    },
    {
      texto: "Qual peça mostra o seu rosto numa chamada de vídeo?",
      opcoes: ["Caixa de som", "Processador", "Webcam", "Mouse"],
      certa: 2,
      explicacao: "A webcam é a câmera do computador.",
    },
  ];

  var atual = 0;
  var form = document.getElementById("quiz-form");
  var legenda = document.getElementById("quiz-pergunta");
  var opcoes = document.getElementById("quiz-opcoes");
  var contador = document.getElementById("quiz-contador");
  var retorno = document.getElementById("quiz-retorno");
  var botaoResponder = document.getElementById("botao-responder");
  var botaoConcluir = document.getElementById("botao-concluir-simulador");
  var resultado = document.getElementById("resultado-simulador");
  var acertouAtual = false;

  function mostrarPergunta() {
    var p = PERGUNTAS[atual];
    acertouAtual = false;
    contador.textContent = "Pergunta " + (atual + 1) + " de " + PERGUNTAS.length;
    legenda.textContent = p.texto;
    opcoes.innerHTML = "";
    p.opcoes.forEach(function (texto, indice) {
      var id = "opcao-" + atual + "-" + indice;
      var linha = document.createElement("div");
      linha.className =
        "flex min-h-[44px] items-center gap-3 rounded-cartilha border-2 border-codigo-texto bg-white px-4 py-2";
      var radio = document.createElement("input");
      radio.type = "radio";
      radio.name = "resposta";
      radio.id = id;
      radio.value = String(indice);
      radio.className = "h-5 w-5 accent-codigo-agua-escuro";
      var rotulo = document.createElement("label");
      rotulo.htmlFor = id;
      rotulo.className = "flex-1 cursor-pointer";
      rotulo.textContent = texto;
      linha.appendChild(radio);
      linha.appendChild(rotulo);
      opcoes.appendChild(linha);
    });
    botaoResponder.querySelector("span").textContent = "Responder";
  }

  function terminar() {
    form.hidden = true;
    contador.textContent = PERGUNTAS.length + " de " + PERGUNTAS.length;
    retorno.textContent = "Você acertou todas! Agora clique em Concluí o simulador.";
    botaoConcluir.disabled = false;
    botaoConcluir.focus();
  }

  form.addEventListener("submit", function (evento) {
    evento.preventDefault();
    if (acertouAtual) {
      atual += 1;
      retorno.textContent = "";
      if (atual >= PERGUNTAS.length) terminar();
      else mostrarPergunta();
      return;
    }
    var marcada = form.querySelector('input[name="resposta"]:checked');
    if (!marcada) {
      retorno.textContent = "Escolha uma das opções antes de responder.";
      return;
    }
    var p = PERGUNTAS[atual];
    if (Number(marcada.value) === p.certa) {
      acertouAtual = true;
      retorno.textContent = "Isso mesmo! " + p.explicacao;
      botaoResponder.querySelector("span").textContent = "Próxima";
    } else {
      retorno.textContent = "Quase! Pense de novo e escolha outra opção.";
    }
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

  mostrarPergunta();
})();
