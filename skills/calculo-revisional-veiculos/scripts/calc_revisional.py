#!/usr/bin/env python3
"""Motor de cálculo revisional (Tabela Price) para financiamento de veículos.

Uso:  python3 calc_revisional.py entrada.json [saida.json]
Sem dependências além da biblioteca padrão.

O motor é determinístico: o mesmo JSON de entrada gera sempre o mesmo resultado.
Toda saída grava calc_version, regras_versao, a referência BACEN usada e o hash da entrada,
para que o laudo possa ser reproduzido meses depois (perícia, impugnação).
"""
import hashlib
import json
import sys
from datetime import date, datetime

CALC_VERSION = "1.0.0"
DATA_MODULACAO_DOBRO = date(2021, 3, 30)  # EAREsp 676.608/RS — dobro só para cobranças a partir desta data


# ---------- matemática financeira ----------
def pmt_price(pv, i, n):
    if n <= 0:
        return 0.0
    if i == 0:
        return pv / n
    return pv * i / (1 - (1 + i) ** -n)


def pv_price(pmt, i, n):
    if n <= 0:
        return 0.0
    if i == 0:
        return pmt * n
    return pmt * (1 - (1 + i) ** -n) / i


def rate_from_pmt(pv, pmt, n):
    """Taxa mensal implícita: resolve PMT(pv, i, n) = pmt por bisseção."""
    if pmt * n <= pv:
        return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if pmt_price(pv, mid, n) > pmt:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ---------- datas ----------
def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def add_months(d, n):
    y = d.year + (d.month - 1 + n) // 12
    m = (d.month - 1 + n) % 12 + 1
    dias_mes = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(y, m, min(d.day, dias_mes[m - 1]))


def month_index(d):
    return d.year * 12 + (d.month - 1)


def regime_do_mes(regimes, ano, mes):
    """Regime vigente no mês (último cujo 'inicio' <= primeiro dia do mês). None se não houver."""
    ref = date(ano, mes, 1)
    vigente = None
    for r in regimes:
        if parse_date(r["inicio"]) <= ref:
            vigente = r
    return vigente


def corrigir(valor, d_pagamento, data_base, regimes):
    """Corrige e acrescenta juros simples mês a mês, do mês seguinte ao do pagamento até o mês da data-base.

    Convenção (documentada no laudo): correção composta mês a mês pelo índice do regime vigente em cada mês;
    juros simples = soma das taxas mensais do regime de cada mês × valor corrigido final.
    Retorna (valor_corrigido, juros, meses, meses_sem_regime).
    """
    n = month_index(data_base) - month_index(d_pagamento)
    fator = 1.0
    soma_juros = 0.0
    sem_regime = 0
    for i in range(1, max(n, 0) + 1):
        idx = month_index(d_pagamento) + i
        ano, mes = idx // 12, idx % 12 + 1
        r = regime_do_mes(regimes, ano, mes)
        if r is None:
            sem_regime += 1
            continue
        fator *= 1 + r.get("indice_mensal", 0.0)
        soma_juros += r.get("juros_mensal", 0.0)
    corrigido = valor * fator
    return corrigido, corrigido * soma_juros, max(n, 0), sem_regime


# ---------- cálculo principal ----------
def calcular(dados):
    c = dados["contrato"]
    ref = dados["referencia"]
    data_base = parse_date(dados["data_base"])
    regimes = sorted(dados.get("regimes", []), key=lambda r: r["inicio"])
    rep = dados.get("repeticao", {})
    multiplo_alerta = dados.get("multiplo_alerta", 1.5)

    valor, n = c["valor_financiado"], int(c["parcelas"])
    encargos = c.get("encargos_financiados", 0.0)
    parcela_informada = c.get("parcela_cobrada") or 0.0
    taxa_contr = c.get("taxa_mensal_contratada") or 0.0
    taxa_anual = c.get("taxa_anual_contratada") or 0.0
    taxa_ref = ref["taxa_mensal"]

    parcela_pela_taxa = pmt_price(valor, taxa_contr, n)
    parcela_cobrada = parcela_informada if parcela_informada > 0 else parcela_pela_taxa
    taxa_efetiva = rate_from_pmt(valor, parcela_cobrada, n)
    principal_rev = max(valor - encargos, 0.0)
    parcela_rev = pmt_price(principal_rev, taxa_ref, n)
    dif = parcela_cobrada - parcela_rev

    # datas dos pagamentos
    if dados["pagamentos"].get("datas"):
        datas = [parse_date(x) for x in dados["pagamentos"]["datas"]]
    else:
        pv1 = parse_date(c["primeiro_vencimento"])
        qtd = min(int(dados["pagamentos"]["quantidade_pagas"]), n)
        datas = [add_months(pv1, k) for k in range(qtd)]
    pagas = len(datas)

    dobro_desde = parse_date(rep.get("dobro_a_partir_de", DATA_MODULACAO_DOBRO.isoformat()))
    ma_fe_antes = bool(rep.get("ma_fe_antes", False))
    dobrar = bool(rep.get("aplicar_dobro", True))

    linhas, tot = [], dict(nominal=0.0, corrigido=0.0, juros=0.0, simples=0.0, apurado=0.0, simples_ate=0.0, dobro_apos=0.0)
    sem_regime_total = 0
    prescritas = 0
    for k, d in enumerate(datas, start=1):
        corr, jur, meses, sem_reg = corrigir(dif, d, data_base, regimes)
        sem_regime_total += sem_reg
        total_simples = corr + jur
        mult = 2 if (dobrar and (d >= dobro_desde or ma_fe_antes)) else 1
        apurado = total_simples * mult
        if d < add_months(data_base, -120):
            prescritas += 1
        linhas.append(dict(parcela=k, data_pagamento=d.isoformat(), cobrada=round(parcela_cobrada, 2), revisada=round(parcela_rev, 2),
                           diferenca=round(dif, 2), corrigida=round(corr, 2), juros=round(jur, 2), meses=meses,
                           multiplicador=mult, total_apurado=round(apurado, 2)))
        tot["nominal"] += dif
        tot["corrigido"] += corr
        tot["juros"] += jur
        tot["simples"] += total_simples
        tot["apurado"] += apurado
        if mult == 1:
            tot["simples_ate"] += total_simples
        else:
            tot["dobro_apos"] += apurado

    restantes = n - pagas
    saldo_contratual = pv_price(parcela_cobrada, taxa_efetiva, restantes)
    saldo_revisado = pv_price(parcela_rev, taxa_ref, restantes)

    razao = taxa_efetiva / taxa_ref if taxa_ref > 0 else None
    alertas = []
    if razao is not None and razao >= multiplo_alerta:
        alertas.append(dict(tipo="atencao", codigo="MULTIPLO_MEDIA",
                            msg=f"Taxa efetiva = {razao:.2f}x a taxa de referência (limiar configurado: {multiplo_alerta}x). "
                                "Indício a investigar, NÃO conclusão de abusividade: a taxa média isoladamente não basta como fundamento "
                                "(ver legal-kb; Tema 1.378/STJ pendente). Registrar fundamentos adicionais (captação, spread, risco, garantia, idade do veículo)."))
    if taxa_anual > 0:
        if taxa_anual > 12 * taxa_contr + 1e-9:
            alertas.append(dict(tipo="info", codigo="DUODECUPLO_OK",
                                msg="Taxa anual informada > duodécuplo da mensal: a jurisprudência (Súmula 541/STJ) admite a cobrança da taxa efetiva anual contratada. "
                                    "Tese de capitalização tende a ser fraca."))
        else:
            alertas.append(dict(tipo="atencao", codigo="DUODECUPLO_NAO",
                                msg="Taxa anual informada não supera o duodécuplo da mensal: verificar se há pactuação expressa de capitalização (Súmulas 539/541)."))
    else:
        alertas.append(dict(tipo="atencao", codigo="SEM_TAXA_ANUAL",
                            msg="Contrato sem taxa anual informada: conferir se a capitalização inferior à anual foi expressamente pactuada (Súmula 539/STJ; Tema 953)."))
    if parcela_informada > 0 and abs(parcela_pela_taxa - parcela_informada) > 0.05:
        alertas.append(dict(tipo="atencao", codigo="PARCELA_DIVERGE",
                            msg=f"Parcela cobrada ({parcela_informada:.2f}) difere da calculada pela taxa informada ({parcela_pela_taxa:.2f}): taxa efetiva maior que a declarada."))
    if encargos > 0:
        alertas.append(dict(tipo="info", codigo="ENCARGOS_EXCLUIDOS",
                            msg=f"Encargos financiados excluídos na revisão: {encargos:.2f}. Cada cobrança depende de prova (Temas 618/619/620, 958, 972)."))
    if dif < 0:
        alertas.append(dict(tipo="atencao", codigo="DIF_NEGATIVA",
                            msg="Parcela revisada maior que a cobrada: a taxa de referência é superior à efetiva. Rever a tese antes de ajuizar."))
    if prescritas:
        alertas.append(dict(tipo="atencao", codigo="PRESCRICAO",
                            msg=f"{prescritas} pagamento(s) com mais de 10 anos da data-base. Prazo decenal (CC, art. 205); termo inicial é controverso (cada pagamento x assinatura)."))
    if sem_regime_total:
        alertas.append(dict(tipo="atencao", codigo="SEM_REGIME",
                            msg=f"{sem_regime_total} mês(es) sem regime de correção/juros cadastrado: a atualização desses meses foi ignorada. Completar 'regimes'."))
    if not regimes:
        alertas.append(dict(tipo="atencao", codigo="SEM_REGIMES",
                            msg="Nenhum regime de correção informado: valores 'corrigidos' = nominais. Informar índice e juros conforme o título/tabela do tribunal."))

    entrada_hash = hashlib.sha256(json.dumps(dados, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    r2 = lambda x: round(x, 2)
    return {
        "calc_version": CALC_VERSION,
        "regras_versao": dados.get("regras_versao", "nao-informada"),
        "entrada_sha256": entrada_hash,
        "referencia_usada": ref,
        "resumo": {
            "parcela_cobrada": r2(parcela_cobrada),
            "parcela_pela_taxa_informada": r2(parcela_pela_taxa),
            "parcela_revisada": r2(parcela_rev),
            "diferenca_por_parcela": r2(dif),
            "taxa_efetiva_mensal": round(taxa_efetiva, 6),
            "taxa_efetiva_anual": round((1 + taxa_efetiva) ** 12 - 1, 6),
            "taxa_referencia_mensal": round(taxa_ref, 6),
            "taxa_referencia_anual": round((1 + taxa_ref) ** 12 - 1, 6),
            "razao_efetiva_referencia": None if razao is None else round(razao, 4),
            "parcelas_pagas": pagas,
            "total_pago_a_maior_nominal": r2(tot["nominal"]),
            "total_corrigido": r2(tot["corrigido"]),
            "total_juros": r2(tot["juros"]),
            "indebito_simples_total": r2(tot["simples"]),
            "indebito_pagamentos_antes_da_modulacao": r2(tot["simples_ate"]),
            "indebito_em_dobro_pagamentos_apos_modulacao": r2(tot["dobro_apos"]),
            "indebito_apurado_total": r2(tot["apurado"]),
            "saldo_devedor_contratual": r2(saldo_contratual),
            "saldo_devedor_revisado": r2(saldo_revisado),
            "reducao_saldo_devedor": r2(saldo_contratual - saldo_revisado),
            "data_base": data_base.isoformat(),
        },
        "alertas": alertas,
        "linhas": linhas,
        "convencoes": [
            "Tabela Price (parcelas iguais). SAC, carência e pagamentos irregulares não cobertos.",
            "Correção composta mês a mês e juros simples sobre o valor corrigido, do mês seguinte ao pagamento até o mês da data-base.",
            f"Multiplicador 2 aplicado a pagamentos em/após {dobro_desde.isoformat()} (modulação do EAREsp 676.608/RS), salvo parâmetros em 'repeticao'.",
            "Taxa de referência informada pelo usuário; guardar série, competência, data da consulta e valor bruto.",
        ],
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        dados = json.load(f)
    res = calcular(dados)
    out = json.dumps(res, ensure_ascii=False, indent=2)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(out)
        print("Resultado gravado em", sys.argv[2])
    else:
        print(out)


if __name__ == "__main__":
    main()
