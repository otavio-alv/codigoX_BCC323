// botao "conclui o desafio": envia o post por fetch e mostra o resultado sem recarregar.
// sem javascript, o formulario continua funcionando com o post normal.
(function () {
  "use strict";

  var form = document.getElementById("form-concluir");
  if (!form || !window.CodigoX) return;

  var botao = document.getElementById("botao-concluir");
  var resultado = document.getElementById("resultado");

  function mostrar(html, classe) {
    resultado.innerHTML = "";
    var caixa = document.createElement("div");
    caixa.className = "rounded-cartilha border-3 border-codigo-texto px-4 py-3 font-medium " + classe;
    caixa.innerHTML = html;
    resultado.appendChild(caixa);
  }

  function texto(valor) {
    var span = document.createElement("span");
    span.textContent = valor;
    return span.innerHTML;
  }

  form.addEventListener("submit", async function (evento) {
    evento.preventDefault();
    botao.disabled = true;

    var resposta = await window.CodigoX.enviarJSON(form.action, {});
    var dados = resposta.dados || {};

    if (resposta.ok && dados.ok) {
      form.remove();
      var link = dados.proximo
        ? '<a class="btn btn-primario btn-grande mt-3" href="' + dados.proximo + '">Ir para o próximo desafio</a>'
        : '<a class="btn btn-primario btn-grande mt-3" href="/aluna/">Voltar para a minha trilha</a>';
      mostrar(
        "<p>" + texto(dados.mensagem) + "</p><p>Agora você tem " + texto(String(dados.total)) +
          " pontos.</p>" + link,
        "bg-emerald-50"
      );
    } else {
      botao.disabled = false;
      mostrar("<p>" + texto(dados.erro || "Não deu certo agora. Tente de novo.") + "</p>", "bg-red-50");
    }
  });
})();
