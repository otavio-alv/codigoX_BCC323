// funcoes usadas em varias paginas da plataforma.
(function () {
  "use strict";

  // o token csrf fica numa <meta> do base.html.
  function tokenCsrf() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
  }

  // envia um post com json e devolve {ok, status, dados}.
  // se a internet cair, devolve ok=false e status=0.
  async function enviarJSON(url, dados) {
    try {
      var resposta = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          "X-CSRFToken": tokenCsrf(),
        },
        body: JSON.stringify(dados || {}),
      });
      var corpo = {};
      try {
        corpo = await resposta.json();
      } catch (erro) {
        corpo = {};
      }
      return { ok: resposta.ok, status: resposta.status, dados: corpo };
    } catch (erro) {
      return { ok: false, status: 0, dados: { erro: "Sem conexão. Confira a internet e tente de novo." } };
    }
  }

  window.CodigoX = { tokenCsrf: tokenCsrf, enviarJSON: enviarJSON };
})();
