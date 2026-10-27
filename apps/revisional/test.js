const C = require("./calc.js");
const assert = require("assert");
const near = (a, b, t = 0.01) => assert(Math.abs(a - b) <= t, a + " != " + b);

// PMT clássico: 10.000, 12x, 2% a.m. => 945,60
near(C.pmtPrice(10000, 0.02, 12), 945.596, 0.01);
// PV inverso
near(C.pvPrice(C.pmtPrice(10000, 0.02, 12), 0.02, 12), 10000);
// Taxa implícita
near(C.rateFromPmt(10000, 945.596, 12), 0.02, 1e-6);

// Caso: 30.000 em 48x, parcela cobrada 1.400, referência 1,8% a.m., 20 pagas
const r = C.revisar({ valor: 30000, n: 48, taxaContratada: 0.0199, parcelaPactuada: 1400, taxaReferencia: 0.018, pagas: 20, encargos: 1200, indiceMensal: 0.004, mesesDesdeUltima: 2, dobro: false });
console.log({ taxaEfetiva: r.taxaEfetiva, parcelaRev: r.parcelaRevisada, dif: r.difPorParcela, totalPagoMais: r.totalPagoMais, indebito: r.indebito, reducaoSaldo: r.reducaoSaldo, flags: r.flags.map(f => f.msg.slice(0, 50)) });
assert(r.rows.length === 20);
assert(r.indebito > r.totalPagoMais);
const rd = C.revisar({ valor: 30000, n: 48, taxaContratada: 0.0199, parcelaPactuada: 1400, taxaReferencia: 0.018, pagas: 20, encargos: 1200, indiceMensal: 0.004, mesesDesdeUltima: 2, dobro: true });
near(rd.indebito, r.indebito * 2);
// Sem diferença: taxa contratada = referência, sem encargos => zero
const z = C.revisar({ valor: 10000, n: 12, taxaContratada: 0.02, taxaReferencia: 0.02, pagas: 6 });
near(z.totalPagoMais, 0, 0.001);
// Saldo ao pagar tudo
const all = C.revisar({ valor: 10000, n: 12, taxaContratada: 0.02, taxaReferencia: 0.01, pagas: 12 });
near(all.saldoContratual, 0);
console.log("OK");
