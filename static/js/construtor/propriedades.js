// painel de propriedades do componente selecionado no editor de telas.
// uso: propriedades.renderizar(caixa, componente, opcoes, aomudar)
//   opcoes: {cores: [{valor, nome}], tamanhos: [{valor, nome}], galeria: [{nome, url}]}
//   aomudar(chave, valor) e chamado a cada mudanca.
(function () {
  "use strict";

  var NOMES = {
    rotulo: "Rótulo",
    botao: "Botão",
    caixa_texto: "Caixa de texto",
    imagem: "Imagem",
    arranjo_horizontal: "Arranjo horizontal",
    arranjo_vertical: "Arranjo vertical",
  };

  var ROTULOS = {
    texto: "Texto",
    dica: "Dica dentro da caixa",
    cor_fundo: "Cor de fundo",
    cor_texto: "Cor do texto",
    tamanho: "Tamanho",
    imagem: "Imagem da galeria",
  };

  // ordem em que as propriedades aparecem no painel
  var ORDEM = ["texto", "dica", "senha", "cor_fundo", "cor_texto", "tamanho", "imagem"];

  function el(tag, classe, texto) {
    var no = document.createElement(tag);
    if (classe) no.className = classe;
    if (texto !== undefined) no.textContent = texto;
    return no;
  }

  function campoTexto(chave, valor, aoMudar) {
    var bloco = el("div");
    var rotulo = el("label", "rotulo", ROTULOS[chave]);
    rotulo.htmlFor = "prop-" + chave;
    var entrada = el("input", "campo");
    entrada.type = "text";
    entrada.id = "prop-" + chave;
    entrada.maxLength = 60;
    entrada.value = valor || "";
    entrada.addEventListener("input", function () {
      aoMudar(chave, entrada.value);
    });
    bloco.appendChild(rotulo);
    bloco.appendChild(entrada);
    return bloco;
  }

  function campoSenha(valor, aoMudar) {
    var bloco = el("div", "flex items-center gap-3 rounded-cartilha border-2 border-codigo-texto bg-white p-3");
    var caixa = el("input", "h-6 w-6 accent-codigo-agua-escuro");
    caixa.type = "checkbox";
    caixa.id = "prop-senha";
    caixa.checked = valor === true;
    caixa.addEventListener("change", function () {
      aoMudar("senha", caixa.checked);
    });
    var rotulo = el("label", "font-medium", "Senha: esconder o que for digitado");
    rotulo.htmlFor = "prop-senha";
    bloco.appendChild(caixa);
    bloco.appendChild(rotulo);
    return bloco;
  }

  function campoCor(chave, valor, cores, aoMudar) {
    var grupo = el("fieldset");
    grupo.appendChild(el("legend", "rotulo", ROTULOS[chave]));
    var lista = el("div", "flex flex-wrap gap-2");
    cores.forEach(function (cor, i) {
      var id = "prop-" + chave + "-" + i;
      var radio = el("input", "peer sr-only");
      radio.type = "radio";
      radio.name = "prop-" + chave;
      radio.id = id;
      radio.value = cor.valor;
      radio.checked = cor.valor === valor;
      radio.addEventListener("change", function () {
        aoMudar(chave, cor.valor);
      });
      var rotulo = el(
        "label",
        "block h-11 w-11 cursor-pointer rounded-full border-3 border-codigo-texto shadow-solida-sm " +
          "peer-checked:outline peer-checked:outline-[3px] peer-checked:outline-offset-2 " +
          "peer-checked:outline-codigo-texto peer-focus-visible:ring-4 peer-focus-visible:ring-codigo-amarelo"
      );
      rotulo.htmlFor = id;
      rotulo.style.backgroundColor = cor.valor;
      rotulo.title = cor.nome;
      rotulo.appendChild(el("span", "sr-only", cor.nome));
      var item = el("div", "relative");
      item.appendChild(radio);
      item.appendChild(rotulo);
      lista.appendChild(item);
    });
    grupo.appendChild(lista);
    return grupo;
  }

  function campoTamanho(valor, tamanhos, aoMudar) {
    var bloco = el("div");
    var rotulo = el("label", "rotulo", ROTULOS.tamanho);
    rotulo.htmlFor = "prop-tamanho";
    var lista = el("select", "campo");
    lista.id = "prop-tamanho";
    tamanhos.forEach(function (t) {
      var opcao = el("option", "", t.nome);
      opcao.value = t.valor;
      opcao.selected = t.valor === valor;
      lista.appendChild(opcao);
    });
    lista.addEventListener("change", function () {
      aoMudar("tamanho", lista.value);
    });
    bloco.appendChild(rotulo);
    bloco.appendChild(lista);
    return bloco;
  }

  function campoImagem(valor, galeria, aoMudar) {
    var grupo = el("fieldset");
    grupo.appendChild(el("legend", "rotulo", ROTULOS.imagem));
    var lista = el("div", "grid grid-cols-3 gap-2");
    galeria.forEach(function (img, i) {
      var id = "prop-imagem-" + i;
      var radio = el("input", "peer sr-only");
      radio.type = "radio";
      radio.name = "prop-imagem";
      radio.id = id;
      radio.value = img.nome;
      radio.checked = img.nome === valor;
      radio.addEventListener("change", function () {
        aoMudar("imagem", img.nome);
      });
      var rotulo = el(
        "label",
        "flex cursor-pointer items-center justify-center rounded-cartilha border-2 border-codigo-texto bg-white p-2 " +
          "peer-checked:bg-codigo-amarelo peer-focus-visible:ring-4 peer-focus-visible:ring-codigo-amarelo"
      );
      rotulo.htmlFor = id;
      var figura = el("img", "h-12 w-12");
      figura.src = img.url;
      figura.alt = img.nome.replace(".svg", "");
      rotulo.appendChild(figura);
      var item = el("div");
      item.appendChild(radio);
      item.appendChild(rotulo);
      lista.appendChild(item);
    });
    grupo.appendChild(lista);
    return grupo;
  }

  function renderizar(caixa, componente, opcoes, aoMudar) {
    caixa.innerHTML = "";
    if (!componente) {
      caixa.appendChild(
        el("p", "text-gray-700", "Clique num componente da tela do celular para mudar as propriedades dele.")
      );
      return;
    }
    caixa.appendChild(el("h3", "", "Propriedades: " + (NOMES[componente.tipo] || componente.tipo)));

    var props = componente.props || {};
    var chaves = ORDEM.filter(function (chave) {
      return Object.prototype.hasOwnProperty.call(props, chave);
    });
    if (chaves.length === 0) {
      caixa.appendChild(
        el("p", "text-gray-700", "Este arranjo não tem propriedades. Selecione-o e adicione componentes: eles entram dentro dele.")
      );
    }
    chaves.forEach(function (chave) {
      var valor = props[chave];
      var campo;
      if (chave === "texto" || chave === "dica") campo = campoTexto(chave, valor, aoMudar);
      else if (chave === "senha") campo = campoSenha(valor, aoMudar);
      else if (chave === "cor_fundo" || chave === "cor_texto") campo = campoCor(chave, valor, opcoes.cores, aoMudar);
      else if (chave === "tamanho") campo = campoTamanho(valor, opcoes.tamanhos, aoMudar);
      else if (chave === "imagem") campo = campoImagem(valor, opcoes.galeria, aoMudar);
      if (campo) caixa.appendChild(campo);
    });
  }

  window.Propriedades = { NOMES: NOMES, renderizar: renderizar };
})();
