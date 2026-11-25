// conferencia dos criterios no navegador.
// e a mesma logica de construtor/services.py: as duas precisam dar o mesmo resultado
// (construtor/tests/casos_criterios.json roda nas duas).
// funciona no navegador (window.criterios) e no node (require), usado pelos testes.
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) {
    module.exports = fabrica();
  } else {
    raiz.Criterios = fabrica();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // propriedades de cada tipo e o valor padrao (igual a padroes do services.py)
  var PADROES = {
    rotulo: { texto: "", cor_texto: "#1E1E24", tamanho: "medio" },
    botao: { texto: "Botão", cor_fundo: "#0B7376", cor_texto: "#FFFFFF", tamanho: "medio" },
    caixa_texto: { dica: "", senha: false },
    imagem: { imagem: "" },
    arranjo_horizontal: {},
    arranjo_vertical: {},
  };

  // lista plana com os componentes e os filhos dos arranjos
  function todos(componentes) {
    var saida = [];
    (componentes || []).forEach(function (c) {
      saida.push(c);
      (c.filhos || []).forEach(function (f) {
        saida.push(f);
      });
    });
    return saida;
  }

  function normalizaTexto(valor) {
    var limpo = valor.trim();
    return limpo === "" ? "" : limpo.split(/\s+/).join(" ").toLowerCase();
  }

  function preenchido(valor) {
    if (typeof valor === "string") return valor.trim() !== "";
    return valor !== null && valor !== undefined && valor !== false;
  }

  function valorDe(componente, chave) {
    var props = componente.props || {};
    if (Object.prototype.hasOwnProperty.call(props, chave)) return props[chave];
    var padrao = PADROES[componente.tipo] || {};
    return padrao[chave] === undefined ? null : padrao[chave];
  }

  function bate(valor, esperado) {
    if (esperado === "*") return preenchido(valor);
    if (typeof esperado === "string") {
      return typeof valor === "string" && normalizaTexto(valor) === normalizaTexto(esperado);
    }
    return typeof valor === typeof esperado && valor === esperado;
  }

  function criterioAtendido(criterio, componentes) {
    var tipo = criterio.componente;
    var candidatos = todos(componentes).filter(function (c) {
      return c.tipo === tipo;
    });

    if (criterio.regra === "existe") {
      var esperadas = criterio.props || {};
      return candidatos.some(function (c) {
        return Object.keys(esperadas).every(function (chave) {
          return bate(valorDe(c, chave), esperadas[chave]);
        });
      });
    }
    if (criterio.regra === "alterado") {
      var padrao = PADROES[tipo] || {};
      var chaves = criterio.props || [];
      return candidatos.some(function (c) {
        return chaves.every(function (chave) {
          var original = padrao[chave] === undefined ? null : padrao[chave];
          return valorDe(c, chave) !== original;
        });
      });
    }
    if (criterio.regra === "minimo_filhos") {
      var n = criterio.n === undefined ? 1 : criterio.n;
      return candidatos.some(function (c) {
        return (c.filhos || []).length >= n;
      });
    }
    return false;
  }

  // devolve as dicas dos criterios que falharam (vazia quando esta tudo certo)
  function conferir(criterios, tela) {
    var componentes = (tela && tela.componentes) || [];
    return (criterios || [])
      .filter(function (c) {
        return !criterioAtendido(c, componentes);
      })
      .map(function (c) {
        return c.dica === undefined ? "" : c.dica;
      });
  }

  return { PADROES: PADROES, conferir: conferir, criterioAtendido: criterioAtendido };
});
