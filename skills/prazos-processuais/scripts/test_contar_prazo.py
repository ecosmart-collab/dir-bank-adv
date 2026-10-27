import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from contar_prazo import contar

# 1) 15 dias úteis simples, sem feriado: disponibilização seg 2026-03-02 -> publicação ter 03-03 -> contagem começa qua 03-04
r = contar({"evento": "2026-03-02", "modo": "dje", "prazo": 15, "feriados": ["2026-12-25"]})
assert r["base_contagem"] == "2026-03-03", r
assert r["primeiro_dia_contado"] == "2026-03-04", r
assert r["vencimento_fatal"] == "2026-03-24", r  # 15 úteis: 4,5,6,9,10,11,12,13,16,17,18,19,20,23,24

# 2) disponibilização na sexta -> publicação na segunda
r = contar({"evento": "2026-03-06", "modo": "dje", "prazo": 5, "feriados": ["2026-12-25"]})
assert r["base_contagem"] == "2026-03-09", r
assert r["primeiro_dia_contado"] == "2026-03-10", r
assert r["vencimento_fatal"] == "2026-03-16", r

# 3) feriado no meio pula
r = contar({"evento": "2026-04-01", "modo": "direto", "prazo": 3, "feriados": ["2026-04-03"]})
# base qua 04-01; contagem: qui 04-02 (1), sex 04-03 feriado, seg 04-06 (2), ter 04-07 (3)
assert r["vencimento_fatal"] == "2026-04-07", r

# 4) suspensão 20/12-20/01 pula
r = contar({"evento": "2026-12-17", "modo": "direto", "prazo": 3, "feriados": ["2026-12-25", "2027-01-01"]})
# 12-18 sex (1); 12-19 sáb; suspensão até 01-20; 01-21 qui (2); 01-22 sex (3)
assert r["vencimento_fatal"] == "2027-01-22", r

# 5) dobro
r = contar({"evento": "2026-03-02", "modo": "direto", "prazo": 5, "multiplicador": 2, "feriados": ["2026-12-25"]})
assert r["prazo_dias"] == 10 and any(a.startswith("DOBRO") for a in r["avisos"]), r

# 6) sem feriados gera aviso
r = contar({"evento": "2026-03-02", "modo": "direto", "prazo": 5})
assert any(a.startswith("SEM_FERIADOS") for a in r["avisos"]), r

# 7) data-alvo interna é 2 úteis antes do fatal
r = contar({"evento": "2026-03-02", "modo": "direto", "prazo": 15, "feriados": ["2026-12-25"]})
assert r["vencimento_fatal"] == "2026-03-23" and r["data_alvo_interna"] == "2026-03-19", r

print("OK")
