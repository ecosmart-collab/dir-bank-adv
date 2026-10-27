/* Motor de cálculo revisional — Tabela Price.
 * Todas as taxas em decimal mensal (1,5% a.m. = 0.015).
 * UMD: funciona no navegador (window.Calc) e no Node (module.exports). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Calc = factory();
})(typeof self !== "undefined" ? self : this, function () {
  function pmtPrice(pv, i, n) {
    if (n <= 0) return 0;
    if (i === 0) return pv / n;
    return (pv * i) / (1 - Math.pow(1 + i, -n));
  }

  function pvPrice(pmt, i, n) {
    if (n <= 0) return 0;
    if (i === 0) return pmt * n;
    return (pmt * (1 - Math.pow(1 + i, -n))) / i;
  }

  // Taxa mensal implícita: resolve PMT(pv, i, n) = pmt por bisseção.
  function rateFromPmt(pv, pmt, n) {
    if (pmt * n <= pv) return 0;
    let lo = 0, hi = 1;
    for (let k = 0; k < 200; k++) {
      const mid = (lo + hi) / 2;
      if (pmtPrice(pv, mid, n) > pmt) hi = mid; else lo = mid;
    }
    return (lo + hi) / 2;
  }

  const anualEfetiva = (im) => Math.pow(1 + im, 12) - 1;
  const round2 = (x) => Math.round((x + Number.EPSILON) * 100) / 100;

  /**
   * @param {object} p
   * @param {number} p.valor            valor financiado (inclui encargos embutidos)
   * @param {number} p.n                número de parcelas
   * @param {number} p.taxaContratada   taxa mensal informada no contrato
   * @param {number} [p.taxaAnualContratada] taxa anual informada (teste de capitalização)
   * @param {number} [p.parcelaPactuada] valor da parcela cobrada (se omitido, calcula pela taxa contratada)
   * @param {number} p.taxaReferencia   taxa mensal de referência (ex.: média BACEN na data da contratação)
   * @param {number} p.pagas            parcelas já pagas
   * @param {number} [p.encargos]       tarifas/seguros financiados a excluir (TAC, TEC, prestamista...)
   * @param {number} [p.indiceMensal]   correção monetária mensal sobre os indébitos
   * @param {number} [p.jurosMora]      juros de mora mensais simples (padrão 1% a.m.)
   * @param {number} [p.mesesDesdeUltima] meses entre a última parcela paga e a data-base
   * @param {boolean} [p.dobro]         repetição em dobro (CDC art. 42, parágrafo único)
   */
  function revisar(p) {
    const encargos = p.encargos || 0;
    const indice = p.indiceMensal || 0;
    const mora = p.jurosMora == null ? 0.01 : p.jurosMora;
    const extra = p.mesesDesdeUltima || 0;
    const pagas = Math.min(Math.max(p.pagas || 0, 0), p.n);

    const parcelaContratual = p.parcelaPactuada > 0 ? p.parcelaPactuada : pmtPrice(p.valor, p.taxaContratada, p.n);
    const parcelaPelaTaxaInformada = pmtPrice(p.valor, p.taxaContratada, p.n);
    const taxaEfetiva = rateFromPmt(p.valor, parcelaContratual, p.n);

    const principalRev = Math.max(p.valor - encargos, 0);
    const parcelaRevisada = pmtPrice(principalRev, p.taxaReferencia, p.n);
    const difPorParcela = parcelaContratual - parcelaRevisada;

    const rows = [];
    let totalPagoMais = 0, totalCorrigido = 0, totalJuros = 0;
    for (let k = 1; k <= pagas; k++) {
      const meses = pagas - k + extra;
      const dif = difPorParcela;
      const corrigido = dif * Math.pow(1 + indice, meses);
      const juros = corrigido * mora * meses;
      rows.push({ k, parcelaPaga: parcelaContratual, parcelaRevisada, dif, corrigido, juros, total: corrigido + juros });
      totalPagoMais += dif;
      totalCorrigido += corrigido;
      totalJuros += juros;
    }

    const restantes = p.n - pagas;
    const saldoContratual = pvPrice(parcelaContratual, taxaEfetiva, restantes);
    const saldoRevisado = pvPrice(parcelaRevisada, p.taxaReferencia, restantes);

    const simples = totalCorrigido + totalJuros;
    const indebito = p.dobro ? simples * 2 : simples;

    const razao = p.taxaReferencia > 0 ? taxaEfetiva / p.taxaReferencia : null;
    const flags = [];
    if (razao !== null && razao >= 1.5) {
      flags.push({ tipo: "alerta", msg: "Taxa efetiva " + razao.toFixed(2) + "x a taxa de referência. Parâmetro usual de abusividade: 1,5x (REsp 1.061.530/RS — orientação, não regra fixa; analise o caso)." });
    } else if (razao !== null && razao > 1) {
      flags.push({ tipo: "info", msg: "Taxa efetiva " + razao.toFixed(2) + "x a referência: acima da média, mas abaixo do parâmetro usual de 1,5x." });
    }
    if (p.taxaAnualContratada > 0 && p.taxaAnualContratada > p.taxaContratada * 12 + 1e-9) {
      flags.push({ tipo: "info", msg: "Taxa anual informada maior que 12x a mensal: indício de capitalização mensal expressamente pactuada (STJ admite se contratada). Confira a cláusula." });
    }
    if (p.parcelaPactuada > 0 && Math.abs(parcelaPelaTaxaInformada - p.parcelaPactuada) > 0.05) {
      flags.push({ tipo: "alerta", msg: "Parcela cobrada (" + round2(p.parcelaPactuada) + ") difere da parcela calculada pela taxa informada (" + round2(parcelaPelaTaxaInformada) + "): taxa efetiva maior que a declarada." });
    }
    if (encargos > 0) {
      flags.push({ tipo: "info", msg: "Encargos financiados excluídos na revisão: " + round2(encargos) + ". Verifique a validade de cada cobrança (ex.: tarifas de cadastro e seguros — REsp 1.251.331/RS e 1.639.320/SP)." });
    }

    return {
      parcelaContratual, parcelaPelaTaxaInformada, taxaEfetiva, taxaEfetivaAnual: anualEfetiva(taxaEfetiva),
      parcelaRevisada, difPorParcela, rows, totalPagoMais, totalCorrigido, totalJuros,
      indebito, dobro: !!p.dobro, saldoContratual, saldoRevisado, reducaoSaldo: saldoContratual - saldoRevisado,
      razao, flags, referenciaAnual: anualEfetiva(p.taxaReferencia)
    };
  }

  return { pmtPrice, pvPrice, rateFromPmt, anualEfetiva, revisar, round2 };
});
