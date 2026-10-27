#!/usr/bin/env python3
"""Pseudonimiza dados pessoais em texto antes de enviá-lo a LLMs/serviços externos (e para o repositório).

Uso:
  python3 pseudonimizar.py entrada.txt saida.txt --mapa mapa.json [--nomes "Fulano de Tal" "Maria X"]
  python3 pseudonimizar.py --reverter texto_com_tokens.txt original.txt --mapa mapa.json

Detecta: CPF, CNPJ, e-mail, telefone, placa, CEP, número de contrato e os NOMES informados em --nomes.
(Nomes não são detectáveis de forma confiável por padrão: informe os da parte/cliente/contraparte.)

O 'mapa.json' permite reverter e é DADO PESSOAL: guardar fora do repositório, com acesso restrito,
nunca enviar a serviço externo e apagar quando o caso encerrar. O texto pseudonimizado é o que pode circular.

Limite: é uma rede de segurança por padrões, não garantia de anonimização. Revisar a saída antes de enviar.
"""
import json
import re
import sys

PADROES = [
    ("CNPJ", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b(?=\D|$)")),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("CPF", re.compile(r"(?i)(?<=CPF)(?:\s*(?:n[ºo.°]*|:)?\s*)(\d{11})\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("TEL", re.compile(r"(?:\+55\s?)?\(\d{2}\)\s?9?\d{4}-?\d{4}\b|\b\d{2}\s9\d{4}-?\d{4}\b")),
    ("PLACA", re.compile(r"\b[A-Z]{3}-?\d[A-Z0-9]\d{2}\b")),
    ("CEP", re.compile(r"\b\d{5}-\d{3}\b")),
    ("CONTRATO", re.compile(r"(?i)(?<=contrato)(?:\s*(?:n[ºo.°]*|:)?\s*)([\w./-]*\d[\w./-]*)")),
    ("CONTRATO", re.compile(r"(?i)(?<=CCB)(?:\s*(?:n[ºo.°]*|:)?\s*)([\w./-]*\d[\w./-]*)")),
]


def pseudonimizar(texto, nomes=None, mapa=None):
    mapa = mapa if mapa is not None else {}
    reverso = {v: k for k, v in mapa.items()}  # original -> token
    contadores = {}
    for tok in mapa:
        m = re.match(r"\[([A-Z]+)_(\d+)\]", tok)
        if m:
            contadores[m.group(1)] = max(contadores.get(m.group(1), 0), int(m.group(2)))

    def token(tipo, original):
        if original in reverso:
            return reverso[original]
        contadores[tipo] = contadores.get(tipo, 0) + 1
        t = f"[{tipo}_{contadores[tipo]}]"
        mapa[t] = original
        reverso[original] = t
        return t

    # protege tokens já existentes (idempotência): o padrão CONTRATO, p.ex., casaria dentro de "[CONTRATO_1]"
    protegidos = re.findall(r"\[[A-Z]+_\d+\]", texto)
    for k, p in enumerate(protegidos):
        texto = texto.replace(p, f"\x00{k}\x00", 1)

    for nome in sorted(nomes or [], key=len, reverse=True):
        texto = re.sub(re.escape(nome), lambda m: token("NOME", m.group(0)), texto, flags=re.I)
    for tipo, rx in PADROES:
        def sub(m, tipo=tipo):
            alvo = m.group(1) if m.lastindex else m.group(0)
            if alvo.startswith("[") and alvo.endswith("]"):
                return m.group(0)  # já é token
            if m.lastindex:
                ini = m.start(1) - m.start(0)
                return m.group(0)[:ini] + token(tipo, alvo) + m.group(0)[ini + len(alvo):]
            return token(tipo, alvo)
        texto = rx.sub(sub, texto)
    for k, p in enumerate(protegidos):
        texto = texto.replace(f"\x00{k}\x00", p, 1)
    return texto, mapa


def reverter(texto, mapa):
    for tok in sorted(mapa, key=len, reverse=True):
        texto = texto.replace(tok, mapa[tok])
    return texto


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(2)
    if "--mapa" not in a:
        print("Informe --mapa mapa.json", file=sys.stderr)
        sys.exit(2)
    i = a.index("--mapa")
    caminho_mapa = a[i + 1]
    del a[i:i + 2]
    nomes = []
    if "--nomes" in a:
        j = a.index("--nomes")
        nomes = a[j + 1:]
        a = a[:j]
    if a[0] == "--reverter":
        txt = open(a[1], encoding="utf-8").read()
        mapa = json.load(open(caminho_mapa, encoding="utf-8"))
        open(a[2], "w", encoding="utf-8").write(reverter(txt, mapa))
        print("Texto restaurado em", a[2])
        return
    txt = open(a[0], encoding="utf-8").read()
    try:
        mapa = json.load(open(caminho_mapa, encoding="utf-8"))
    except FileNotFoundError:
        mapa = {}
    novo, mapa = pseudonimizar(txt, nomes, mapa)
    open(a[1], "w", encoding="utf-8").write(novo)
    json.dump(mapa, open(caminho_mapa, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Pseudonimizado: {a[1]} | {len(mapa)} itens no mapa ({caminho_mapa}) — guarde o mapa FORA do repositório.")


if __name__ == "__main__":
    main()
