#!/usr/bin/env python3
"""Monta o RASCUNHO da petição inicial revisional a partir de caso.json (+ saída do motor de cálculo).

Uso:  python3 montar_peca.py caso.json peca.md [--sem-notas] [--kb caminho/kb.yaml]

caso.json: ver references/exemplo_caso.json. O bloco "calculo" é o JSON gerado por
calculo-revisional-veiculos/scripts/calc_revisional.py (cole o resultado inteiro).

Saídas: peca.md (rascunho com banner), peca.relatorio.json (pendências e validação de citações).
Código de saída: 0 = sem pendências bloqueantes; 1 = há campos a preencher ou citações fora da base.

Princípios: o texto jurídico só usa citações da base curada (legal-kb-revisional); os números vêm
do cálculo, nunca digitados; campos faltantes ficam visíveis como [[PREENCHER: ...]].
"""
import importlib.util
import json
import os
import re
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
MODULOS = os.path.join(SKILL, "assets", "modulos")
OPCIONAIS = {"contrato.taxa_anual_texto", "gratuidade_pedido"}  # podem ficar vazios sem virar pendência
ROMANOS = ["I","II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

MODULO_POR_TESE = {
    "juros": "20_juros.md",
    "capitalizacao": "21_capitalizacao.md",
    "tarifas": "22_tarifas.md",
    "seguro": "23_seguro.md",
    "comissao_permanencia": "24_comissao_permanencia.md",
}
ROTULO_TESE = {
    "juros": "taxa de juros remuneratórios",
    "capitalizacao": "capitalização de juros",
    "tarifas": "tarifas e despesas financiadas",
    "seguro": "seguro e pré-gravame",
    "comissao_permanencia": "comissão de permanência",
}


# ---------- formatação ----------
def brl(v):
    s = f"{float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + s


def pct(v):
    return f"{float(v) * 100:.2f}".replace(".", ",") + "%"


def n2(v):
    return f"{float(v):.2f}".replace(".", ",")


def data_br(v):
    try:
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return str(v)


FILTROS = {"brl": brl, "pct": pct, "n2": n2, "data": data_br, "upper": lambda v: str(v).upper()}


def lookup(ctx, caminho):
    cur = ctx
    for parte in caminho.split("."):
        if isinstance(cur, dict) and parte in cur:
            cur = cur[parte]
        else:
            return None
    return cur


def preencher(texto, ctx, pendentes):
    def sub(m):
        chave, _, filtro = m.group(1).strip().partition("|")
        chave, filtro = chave.strip(), filtro.strip()
        v = lookup(ctx, chave)
        if v == "" and chave in OPCIONAIS:
            return ""
        if chave == "valor_causa" and not v:  # 0 não é um valor de causa válido: forçar definição
            v = None
        if v is None or v == "":
            pendentes.append(chave)
            return f"[[PREENCHER: {chave}]]"
        if filtro:
            try:
                return FILTROS[filtro](v)
            except (KeyError, ValueError, TypeError):
                pendentes.append(chave)
                return f"[[PREENCHER: {chave}]]"
        return str(v)
    return re.sub(r"\{\{([^{}]+)\}\}", sub, texto)


# ---------- textos derivados ----------
def derivar(caso):
    r = caso.get("calculo", {}).get("resumo", {})
    d = {}
    d["gratuidade_texto"] = (
        "O(A) autor(a) declara, sob as penas da lei, não possuir condições de arcar com as custas e despesas "
        "do processo sem prejuízo do próprio sustento e de sua família, requerendo os benefícios da gratuidade da justiça "
        "(CPC, art. 98), conforme declaração e documentos anexos."
        if caso.get("gratuidade") else "O(A) autor(a) não requer a gratuidade da justiça e recolherá as custas devidas.")
    d["gratuidade_pedido"] = ", nos termos da declaração anexa" if caso.get("gratuidade") else ""
    d["conciliacao_texto"] = "interesse" if caso.get("conciliacao", True) else "desinteresse"
    ta = caso.get("contrato", {}).get("taxa_anual")
    d["contrato"] = {"taxa_anual_texto": f" e taxa anual de {pct(ta)}" if ta else ""}
    obrig = [ROTULO_TESE[t] for t in caso.get("teses", []) if t in ROTULO_TESE]
    d["obrigacoes_controvertidas"] = "; ".join(obrig) + "." if obrig else ""
    dob = r.get("indebito_em_dobro_pagamentos_apos_modulacao", 0) or 0
    if dob > 0 and caso.get("calculo", {}).get("resumo"):
        simples_antes = r.get("indebito_pagamentos_antes_da_modulacao", 0) or 0
        d["dobro_texto"] = (
            "Em relação aos pagamentos efetuados a partir de 30/3/2021, requer-se a restituição em dobro, nos termos do art. 42, "
            f"parágrafo único, do CDC, totalizando {brl(dob)} (valor já dobrado, atualizado)."
            + (f" Os pagamentos anteriores a essa data serão restituídos de forma simples, no valor de {brl(simples_antes)}." if simples_antes > 0 else ""))
    else:
        d["dobro_texto"] = "Requer-se a restituição na forma simples."
    t = caso.get("tutela", {})
    itens = []
    if t.get("depositar_incontroverso"):
        itens.append(f"autorizar o pagamento (ou o depósito judicial) das parcelas vincendas no valor incontroverso de {brl(r['parcela_revisada']) if 'parcela_revisada' in r else '[[PREENCHER: calculo.resumo.parcela_revisada]]'}, enquanto perdurar a discussão;")
    if t.get("abstencao_negativacao"):
        itens.append("determinar que o réu se abstenha de inscrever o nome do(a) autor(a) em cadastros de inadimplentes, ou, se já inscrito, promova a exclusão do apontamento relativo ao contrato discutido;")
    if t.get("manutencao_posse"):
        itens.append("determinar que o réu se abstenha de promover ou requerer a busca e apreensão do veículo, mantendo-se o(a) autor(a) na posse do bem.")
    d["tutela_pedidos"] = "\n".join(f"{chr(97 + i)}) {x}" for i, x in enumerate(itens)) if itens else ""
    m = []
    for t_ in caso.get("teses", []):
        if t_ == "juros":
            m.append("revisar a taxa de juros remuneratórios, reduzindo-a para a taxa média de mercado vigente na data da contratação;")
        elif t_ == "capitalizacao":
            m.append("afastar a capitalização de juros não pactuada, recalculando o débito;")
        elif t_ == "tarifas":
            m.append("declarar a nulidade das tarifas e despesas impugnadas, excluindo-as do valor financiado;")
        elif t_ == "seguro":
            m.append("declarar a nulidade da contratação do seguro e do pré-gravame, excluindo-os do financiamento;")
        elif t_ == "comissao_permanencia":
            m.append("afastar a cumulação indevida de encargos na inadimplência, limitando a comissão de permanência aos parâmetros jurisprudenciais;")
    m.append("recalcular o contrato e o saldo devedor segundo os parâmetros acima;")
    m.append("condenar o réu a restituir os valores pagos a maior, na forma simples ou em dobro conforme o caso, com correção monetária e juros;")
    m.append("compensar eventual crédito do(a) autor(a) com o saldo devedor remanescente.")
    d["pedidos_merito"] = "\n".join(f"   {i + 1}. {x}" for i, x in enumerate(m))
    return d


def mesclar(base, extra):
    """Mescla 'extra' em 'base'; valores já preenchidos em 'base' (informados pelo advogado) prevalecem."""
    out = dict(base)
    for k, v in extra.items():
        if k not in out or out[k] in (None, ""):
            out[k] = v
        elif isinstance(v, dict) and isinstance(out[k], dict):
            out[k] = mesclar(out[k], v)
    return out


# ---------- citações ----------
def validar_citacoes(texto, kb_arg):
    candidatos = [kb_arg, os.environ.get("LEGAL_KB_PATH"),
                  os.path.join(SKILL, "..", "legal-kb-revisional", "references", "kb.yaml")]
    kb = next((c for c in candidatos if c and os.path.exists(c)), None)
    val = os.path.join(os.path.dirname(kb or ""), "..", "scripts", "validar_citacoes.py") if kb else None
    if not kb or not os.path.exists(val):
        return None, "Base legal-kb-revisional não encontrada: validação de citações NÃO executada. Rode a skill legal-kb-revisional antes de enviar."
    spec = importlib.util.spec_from_file_location("validar_citacoes", val)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import yaml
    with open(kb, encoding="utf-8") as f:
        kbd = yaml.safe_load(f)
    return mod.validar(texto, kbd), kbd["meta"]["kb_versao"]


# ---------- principal ----------
def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    sem_notas = "--sem-notas" in args
    kb_arg = None
    if "--kb" in args:
        i = args.index("--kb")
        kb_arg = args[i + 1]
        del args[i:i + 2]
    args = [a for a in args if a != "--sem-notas"]
    with open(args[0], encoding="utf-8") as f:
        caso = json.load(f)
    saida = args[1]
    # "calculo_arquivo": caminho (relativo ao caso.json) da saída do motor de cálculo
    if "calculo" not in caso and caso.get("calculo_arquivo"):
        p = os.path.join(os.path.dirname(os.path.abspath(args[0])), caso["calculo_arquivo"])
        with open(p, encoding="utf-8") as f:
            caso["calculo"] = json.load(f)

    ctx = mesclar(caso, derivar(caso))
    teses = [t for t in caso.get("teses", []) if t in MODULO_POR_TESE]

    # numeração das seções
    n = 3  # I, II, III já usados (gratuidade, conciliação, fatos)
    n += 1
    secoes = {"direito": ROMANOS[n - 1]}
    n += 1
    secoes["incontroverso"] = ROMANOS[n - 1]
    n += 1
    secoes["indebito"] = ROMANOS[n - 1]
    if caso.get("tutela") and any(caso["tutela"].values()):
        n += 1
        secoes["tutela"] = ROMANOS[n - 1]
    n += 1
    secoes["pedidos"] = ROMANOS[n - 1]
    ctx.update({f"secao_{k}": v for k, v in secoes.items()})

    def ler(nome):
        with open(os.path.join(MODULOS, nome), encoding="utf-8") as f:
            return f.read().strip()

    partes = [ler("00_cabecalho.md"), ler("10_fatos.md"),
              f"## {secoes['direito']}. DO DIREITO\n\nO contrato é de consumo e se submete ao Código de Defesa do Consumidor, sendo nulas as cláusulas que estabeleçam obrigações iníquas ou abusivas, que coloquem o consumidor em desvantagem exagerada (CDC, art. 51, IV)."]
    partes += [ler(MODULO_POR_TESE[t]) for t in teses]
    partes += [ler("30_incontroverso.md"), ler("35_indebito.md")]
    if "tutela" in secoes:
        partes.append(ler("40_tutela.md"))
    partes.append(ler("50_pedidos.md"))
    texto = "\n\n".join(partes)

    pendentes = []
    texto = preencher(texto, ctx, pendentes)
    if sem_notas:
        texto = re.sub(r"\n*<!-- NOTA AO ADVOGADO:.*?-->", "", texto, flags=re.S)
    notas = len(re.findall(r"<!-- NOTA AO ADVOGADO:", texto))

    cit, kbv = validar_citacoes(texto, kb_arg)
    fora = [c for c in (cit or []) if c["situacao"] == "FORA_DA_BASE"]
    avisos = sorted({a for c in (cit or []) if c["situacao"] == "NA_BASE" for a in c["avisos"]})

    banner = ("> **RASCUNHO — NÃO PROTOCOLAR.** Gerado com apoio de IA em "
              f"{datetime.now().strftime('%d/%m/%Y')}. Exige revisão integral e assinatura do advogado responsável "
              "(Recomendação CFOAB 001/2024). Citações limitadas à base legal-kb"
              f"{' (' + kbv + ')' if isinstance(kbv, str) and cit is not None else ''}; "
              "confira cada uma no portal oficial. Campos [[PREENCHER]] e notas ao advogado devem ser resolvidos e removidos.\n\n")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(banner + texto + "\n")

    relatorio = {
        "arquivo": saida,
        "campos_a_preencher": sorted(set(pendentes)),
        "notas_ao_advogado": notas,
        "teses_incluidas": teses,
        "citacoes": cit if cit is not None else kbv,
        "citacoes_fora_da_base": [c["trecho"] for c in fora],
        "avisos_de_status_e_conferencia": avisos,
    }
    with open(saida.rsplit(".", 1)[0] + ".relatorio.json", "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"Rascunho: {saida}")
    print(f"Campos a preencher: {len(set(pendentes))} | Notas ao advogado: {notas} | Citações fora da base: {len(fora)}")
    if cit is None:
        print("ATENÇÃO:", kbv)
    sys.exit(1 if (pendentes or fora or cit is None) else 0)


if __name__ == "__main__":
    main()
