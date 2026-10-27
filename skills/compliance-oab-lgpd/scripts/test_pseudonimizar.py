#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from pseudonimizar import pseudonimizar, reverter

t = ("Maria da Silva Souza, CPF 123.456.789-09, e-mail maria@exemplo.com, tel. (48) 99999-1234, "
     "placa ABC1D23 (e ABC-1234), CEP 88745-000, contrato nº 123456-7/2022 com o Banco XYZ (CNPJ 12.345.678/0001-95). "
     "Maria da Silva Souza pagou a parcela. CPF 98765432100 também.")
novo, mapa = pseudonimizar(t, nomes=["Maria da Silva Souza"])
for proibido in ["123.456.789-09", "maria@exemplo.com", "99999-1234", "ABC1D23", "ABC-1234", "88745-000", "123456-7/2022", "12.345.678/0001-95", "Maria da Silva", "98765432100"]:
    assert proibido not in novo, (proibido, novo)
assert novo.count("[NOME_1]") == 2, novo  # mesmo nome, mesmo token
assert reverter(novo, mapa) == t, (reverter(novo, mapa), t)
# idempotente: reaplicar não altera tokens
novo2, _ = pseudonimizar(novo, nomes=["Maria da Silva Souza"], mapa=dict(mapa))
assert novo2 == novo
print("OK")
print(novo)
