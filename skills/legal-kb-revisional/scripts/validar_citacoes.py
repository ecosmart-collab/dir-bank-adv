#!/usr/bin/env python3
"""Valida as citações de um texto (rascunho de peça) contra a base curada kb.yaml.

Uso:  python3 validar_citacoes.py texto.md [--kb caminho/kb.yaml] [--json]
      cat texto.md | python3 validar_citacoes.py -

Detecta: Súmula N, Tema(s) N, REsp/AREsp/EAREsp N/UF, ADI(s) N, Lei N/AAAA, CC art. 205, CPC art. 330.
Códigos de saída: 0 = todas as citações estão na base; 1 = há citação fora da base; 2 = erro de uso.

Por que existe: peças com jurisprudência inexistente ou desatualizada já geraram multas a advogados.
A regra do escritório é: nenhuma citação entra em peça se não estiver na base curada.
"""
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("Instale PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KB = os.path.join(HERE, "..", "references", "kb.yaml")

NUM = r"\d{1,4}(?:\.\d{3})*"


def to_int(s):
    return int(s.replace(".", ""))


def expandir(seq):
    """'24 a 28', '618/619', '618, 619 e 620' -> lista de ints."""
    partes = re.split(r"\s*(,|e|/|a|–|-)\s*", seq)
    nums, sep_prev, out = [], None, []
    for p in partes:
        if re.fullmatch(NUM, p or ""):
            n = to_int(p)
            if sep_prev in ("a", "–", "-") and out:
                out.extend(range(out[-1] + 1, n + 1))
            else:
                out.append(n)
        else:
            sep_prev = p
    return out


def extrair(texto):
    cit = []  # (tipo, numero, trecho)
    # Súmulas
    for m in re.finditer(r"S[úu]mulas?\s*(?:n[ºo.°]*\s*)?((?:%s)(?:\s*(?:,|e|/|a)\s*(?:%s))*)" % (NUM, NUM), texto, re.I):
        for n in expandir(m.group(1)):
            cit.append(("sumula", n, m.group(0)))
    # Temas
    for m in re.finditer(r"Temas?\s*(?:Repetitivos?\s*)?(?:n[ºo.°]*\s*)?((?:%s)(?:\s*(?:,|e|/|a|–|-)\s*(?:%s))*)" % (NUM, NUM), texto, re.I):
        for n in expandir(m.group(1)):
            cit.append(("tema", n, m.group(0)))
    # REsp, AREsp, EAREsp
    for m in re.finditer(r"\b(?:E?A?REsp|EREsp)\s*(?:n[ºo.°]*\s*)?(\d{1,3}(?:\.\d{3})+|\d{3,7})\s*/\s*[A-Z]{2}", texto):
        cit.append(("precedente", to_int(m.group(1)), m.group(0)))
    # ADIs
    for m in re.finditer(r"ADIs?\s*(?:n[ºo.°]*\s*)?((?:\d{4})(?:\s*(?:,|e)\s*\d{4})*)", texto):
        for n in re.findall(r"\d{4}", m.group(1)):
            cit.append(("decisao_stf", int(n), m.group(0)))
    # Leis
    for m in re.finditer(r"Lei\s*(?:n[ºo.°]*\s*)?(\d{1,2}\.?\d{3})\s*/\s*(?:19|20)?\d{2}", texto):
        cit.append(("lei", to_int(m.group(1)), m.group(0)))
    # Artigos específicos conhecidos
    if re.search(r"art(?:igo|\.)\s*205\s*(?:do\s*)?(?:CC|C[óo]digo Civil)", texto, re.I):
        cit.append(("lei", 205, "CC art. 205"))
    if re.search(r"art(?:igo|\.)\s*330\s*(?:,|do)?\s*(?:§|CPC|C[óo]digo de Processo)", texto, re.I):
        cit.append(("lei", 330, "CPC art. 330"))
    return cit


def indexar(kb):
    idx = {}
    for e in kb["entradas"]:
        for n in e.get("numeros", []):
            idx.setdefault((e["tipo"], n), []).append(e)
        # 'precedentes' lista números de REsp/AREsp/EAREsp associados à entrada (ex.: paradigma de um tema)
        for n in e.get("precedentes", []):
            idx.setdefault(("precedente", n), []).append(e)
    return idx


def validar(texto, kb):
    idx = indexar(kb)
    resultado, vistos = [], set()
    for tipo, n, trecho in extrair(texto):
        chave = (tipo, n)
        if chave in vistos:
            continue
        vistos.add(chave)
        encontrados = idx.get(chave)
        if not encontrados:
            resultado.append(dict(tipo=tipo, numero=n, trecho=trecho, situacao="FORA_DA_BASE",
                                  acao="Remover do texto ou pedir ao advogado que confira no portal oficial e inclua na base."))
            continue
        e = encontrados[0]
        avisos = []
        if e["status"] in ("pendente", "controverso", "superado", "mudou"):
            avisos.append(f"status '{e['status']}': tratar com cautela e dizer isso na peça/parecer")
        if e["status"] == "superado":
            avisos.append("NÃO usar como fundamento")
        if not e.get("verificado_em"):
            avisos.append("não conferida no portal oficial (verificado_em vazio): só em rascunho")
        resultado.append(dict(tipo=tipo, numero=n, trecho=trecho, situacao="NA_BASE", id=e["id"], status=e["status"],
                              verificado_em=e.get("verificado_em"), avisos=avisos))
    return resultado


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    kb_path = DEFAULT_KB
    if "--kb" in args:
        i = args.index("--kb")
        kb_path = args[i + 1]
        del args[i:i + 2]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    texto = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
    with open(kb_path, encoding="utf-8") as f:
        kb = yaml.safe_load(f)
    res = validar(texto, kb)
    fora = [r for r in res if r["situacao"] == "FORA_DA_BASE"]
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(f"Base: {kb['meta']['kb_versao']} | citações distintas: {len(res)} | fora da base: {len(fora)}")
        for r in res:
            if r["situacao"] == "FORA_DA_BASE":
                print(f"  [FORA DA BASE] {r['trecho']!r} ({r['tipo']} {r['numero']}) -> {r['acao']}")
            else:
                aviso = ("  | " + "; ".join(r["avisos"])) if r["avisos"] else ""
                print(f"  [ok] {r['id']} (status {r['status']}){aviso}")
    sys.exit(1 if fora else 0)


if __name__ == "__main__":
    main()
