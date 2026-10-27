#!/usr/bin/env python3
"""Testes do motor revisional. Rodar: python3 test_calc.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import calc_revisional as C

def near(a, b, t=0.01):
    assert abs(a - b) <= t, f"{a} != {b}"

# PMT / PV / taxa implícita
near(C.pmt_price(10000, 0.02, 12), 945.596, 0.01)
near(C.pv_price(C.pmt_price(10000, 0.02, 12), 0.02, 12), 10000)
near(C.rate_from_pmt(10000, 945.596, 12), 0.02, 1e-6)

# Caso exemplo (mesmos números da calculadora web): taxa efetiva 3,9347% a.m.; parcela revisada 901,13
ex = json.load(open(os.path.join(os.path.dirname(__file__), "exemplo_entrada.json"), encoding="utf-8"))
r = C.calcular(ex)
s = r["resumo"]
near(s["taxa_efetiva_mensal"], 0.039347, 1e-5)
near(s["parcela_revisada"], 901.13, 0.01)
near(s["diferenca_por_parcela"], 498.87, 0.01)
near(s["total_pago_a_maior_nominal"], 20 * 498.8676, 0.5)
assert len(r["linhas"]) == 20
assert any(a["codigo"] == "MULTIPLO_MEDIA" for a in r["alertas"])
assert any(a["codigo"] == "SEM_TAXA_ANUAL" for a in r["alertas"])

# Modulação do dobro: pagamentos antes de 30/3/2021 ficam simples; depois, em dobro
ex2 = json.loads(json.dumps(ex))
ex2["contrato"]["primeiro_vencimento"] = "2020-12-10"
ex2["pagamentos"] = {"quantidade_pagas": 6}
r2 = C.calcular(ex2)
mults = [l["multiplicador"] for l in r2["linhas"]]
assert mults == [1, 1, 1, 1, 2, 2], mults  # dez/20 a mar/21 (dia 10, antes de 30/3) simples; abr e mai/21 em dobro
print("OK")
