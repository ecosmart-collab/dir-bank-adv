#!/usr/bin/env python3
"""Valida a extração de um contrato de financiamento (JSON conforme references/schema_contrato.json).

Uso:  python3 validar_extracao.py extracao.json [--calc-out entrada_calculo.json]

O que faz:
  1. Confere a estrutura (cada campo com valor, confiança, página e trecho de sustentação).
  2. Lista os 'campos a conferir': críticos, nulos, de confiança média/baixa, ou sem trecho.
  3. Roda checagens de consistência (parcela x taxa, duodécuplo, CET, encargos x valor liberado, datas).
  4. Informa o status: PENDENTE_CONFERENCIA até 'conferencia_humana.conferido_por' ser preenchido.
  5. Opcionalmente gera o esqueleto de entrada para calc_revisional.py (sem taxa de referência).

Códigos de saída: 0 = sem erros estruturais; 1 = erros estruturais; 2 = erro de uso.
A IA extrai; o código valida; o humano confere. Nada daqui vai para peça sem a conferência.
"""
import json
import re
import sys

CRITICOS = [
    ("financiamento", "valor_total_financiado"), ("financiamento", "numero_parcelas"),
    ("financiamento", "valor_parcela"), ("financiamento", "primeiro_vencimento"),
    ("contrato", "data_contratacao"), ("taxas", "juros_mensal"), ("taxas", "juros_anual"),
]
CONF = {"alta", "media", "baixa"}


def pmt(pv, i, n):
    return pv / n if i == 0 else pv * i / (1 - (1 + i) ** -n)


def val(d, sec, k):
    c = d.get(sec, {}).get(k)
    return c.get("valor") if isinstance(c, dict) else None


def validar(d):
    erros, conferir, alertas = [], [], []

    # 1) estrutura
    for sec in ("documento", "contrato", "financiamento", "taxas"):
        if sec not in d:
            erros.append(f"Seção obrigatória ausente: {sec}")
    campos = []
    for sec, conteudo in d.items():
        if sec in ("documento", "conferencia_humana", "encargos"):
            continue
        if isinstance(conteudo, dict):
            for k, c in conteudo.items():
                campos.append((f"{sec}.{k}", c))
    for i, e in enumerate(d.get("encargos", [])):
        campos.append((f"encargos[{i}]({e.get('tipo')})", e))
    for nome, c in campos:
        if not isinstance(c, dict) or "valor" not in c or "confianca" not in c:
            erros.append(f"{nome}: campo deve ter 'valor' e 'confianca'")
            continue
        if c["confianca"] not in CONF:
            erros.append(f"{nome}: confianca inválida ({c['confianca']!r})")
        if c["valor"] is not None and not c.get("trecho"):
            conferir.append((nome, "sem trecho literal de sustentação"))
        if c["valor"] is not None and c.get("pagina") is None:
            conferir.append((nome, "sem página"))
        if c["valor"] is None and not c.get("nao_encontrado"):
            conferir.append((nome, "valor nulo sem marcar nao_encontrado"))
        if c["confianca"] in ("media", "baixa") and c["valor"] is not None:
            conferir.append((nome, f"confiança {c['confianca']}"))

    # críticos: sempre listar os ausentes; presentes entram na conferência humana obrigatória
    for sec, k in CRITICOS:
        v = val(d, sec, k)
        if v is None:
            conferir.append((f"{sec}.{k}", "campo crítico ausente/não encontrado"))

    # 2) consistência
    vf, n, vp = val(d, "financiamento", "valor_total_financiado"), val(d, "financiamento", "numero_parcelas"), val(d, "financiamento", "valor_parcela")
    im, ia = val(d, "taxas", "juros_mensal"), val(d, "taxas", "juros_anual")
    if all(isinstance(x, (int, float)) for x in (vf, n, vp)) and n > 0:
        if vp * n < vf:
            alertas.append("Soma das parcelas menor que o valor financiado: provável erro de leitura (valor, parcelas ou parcela).")
        if isinstance(im, (int, float)) and im > 0:
            calc = pmt(vf, im, int(n))
            if abs(calc - vp) / vp > 0.01:
                alertas.append(f"Parcela lida ({vp:.2f}) difere da calculada pela taxa mensal lida ({calc:.2f}) em mais de 1%: "
                               "conferir taxa, valor financiado ou nº de parcelas. Se tudo estiver correto, a diferença indica taxa efetiva maior que a declarada.")
    if isinstance(im, (int, float)) and isinstance(ia, (int, float)):
        if im > 1 or ia > 10:
            alertas.append("Taxa fora do formato fração (ex.: 1,99% deve ser 0.0199): conferir a conversão.")
        elif ia > 12 * im + 1e-9:
            alertas.append("Taxa anual > 12x a mensal (duodécuplo): em tese há pactuação de capitalização (Súmula 541/STJ).")
        elif ia > 0:
            alertas.append("Taxa anual não supera o duodécuplo da mensal: verificar cláusula expressa de capitalização (Súmula 539/STJ).")
    elif im is not None and ia is None:
        alertas.append("Taxa anual não encontrada: verificar se o contrato realmente a omite (relevante para capitalização).")
    cm = val(d, "taxas", "cet_mensal")
    if isinstance(cm, (int, float)) and isinstance(im, (int, float)) and cm < im:
        alertas.append("CET mensal menor que a taxa de juros mensal: improvável, conferir leitura.")
    dc, pv1 = val(d, "contrato", "data_contratacao"), val(d, "financiamento", "primeiro_vencimento")
    for nome, x in (("data_contratacao", dc), ("primeiro_vencimento", pv1)):
        if x is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(x)):
            erros.append(f"{nome}: formato esperado AAAA-MM-DD, recebido {x!r}")
    if dc and pv1 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(dc)) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(pv1)) and pv1 < dc:
        alertas.append("Primeiro vencimento anterior à data de contratação: conferir datas.")
    liberado = val(d, "financiamento", "valor_liberado")
    fin = [e for e in d.get("encargos", []) if e.get("financiado") and isinstance(e.get("valor"), (int, float))]
    soma = sum(e["valor"] for e in fin)
    if isinstance(vf, (int, float)) and isinstance(liberado, (int, float)):
        dif = vf - liberado
        if abs(dif - soma) > max(1.0, 0.01 * vf):
            alertas.append(f"Valor financiado - valor liberado = {dif:.2f}, mas encargos financiados somam {soma:.2f}: "
                           "pode haver encargo não extraído (IOF, seguro, tarifa) ou erro de leitura.")
    placa = val(d, "garantia", "veiculo_placa")
    if isinstance(placa, str) and not re.fullmatch(r"[A-Z]{3}-?\d[A-Z0-9]\d{2}", placa.upper()):
        alertas.append(f"Placa em formato incomum ({placa}): conferir.")
    for e in d.get("encargos", []):
        if e.get("tipo") in ("tac", "tec") and isinstance(dc, str) and dc >= "2008-04-30":
            alertas.append("TAC/TEC cobradas em contrato posterior a 30/4/2008: ponto forte, conferir a data (Temas 618/619; Súmula 565).")
            break
    seg = d.get("seguro", {})
    if val(d, "seguro", "contratado") and val(d, "seguro", "documento_apartado") is False:
        alertas.append("Seguro contratado sem documento apartado: verificar opção de escolha (Tema 972).")

    # 3) status
    ch = d.get("conferencia_humana") or {}
    status = "CONFERIDO" if ch.get("conferido_por") and ch.get("conferido_em") else "PENDENTE_CONFERENCIA"
    return dict(status=status, erros=erros, campos_a_conferir=[{"campo": a, "motivo": b} for a, b in conferir],
                alertas=alertas, encargos_financiados_total=round(soma, 2))


def gerar_entrada_calculo(d):
    g = lambda s, k: val(d, s, k)
    enc = sum(e["valor"] for e in d.get("encargos", []) if e.get("financiado") and isinstance(e.get("valor"), (int, float)))
    return {
        "_aviso": "Esqueleto gerado da extração. Faltam: referencia (série BACEN da competência da contratação), data_base, regimes e pagamentos.",
        "caso": {"cliente": "PREENCHER (use pseudônimo)", "contrato": g("contrato", "numero")},
        "contrato": {
            "valor_financiado": g("financiamento", "valor_total_financiado"),
            "parcelas": g("financiamento", "numero_parcelas"),
            "taxa_mensal_contratada": g("taxas", "juros_mensal"),
            "taxa_anual_contratada": g("taxas", "juros_anual"),
            "parcela_cobrada": g("financiamento", "valor_parcela"),
            "data_contratacao": g("contrato", "data_contratacao"),
            "primeiro_vencimento": g("financiamento", "primeiro_vencimento"),
            "encargos_financiados": round(enc, 2),
        },
        "pagamentos": {"quantidade_pagas": None},
        "referencia": {"serie": "SGS 25471", "competencia": (g("contrato", "data_contratacao") or "")[:7] or None,
                       "data_consulta": None, "valor_bruto_percentual": None, "taxa_mensal": None},
        "data_base": None,
        "regimes": [],
        "repeticao": {"aplicar_dobro": True, "dobro_a_partir_de": "2021-03-30", "ma_fe_antes": False},
        "multiplo_alerta": 1.5,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    calc_out = None
    if "--calc-out" in args:
        i = args.index("--calc-out")
        calc_out = args[i + 1]
        del args[i:i + 2]
    with open(args[0], encoding="utf-8") as f:
        d = json.load(f)
    r = validar(d)
    print(f"Status: {r['status']}")
    print(f"Erros estruturais: {len(r['erros'])} | Campos a conferir: {len(r['campos_a_conferir'])} | Alertas: {len(r['alertas'])}")
    for e in r["erros"]:
        print("  [ERRO]", e)
    for c in r["campos_a_conferir"]:
        print(f"  [CONFERIR] {c['campo']}: {c['motivo']}")
    for a in r["alertas"]:
        print("  [ALERTA]", a)
    if calc_out and not r["erros"]:
        with open(calc_out, "w", encoding="utf-8") as f:
            json.dump(gerar_entrada_calculo(d), f, ensure_ascii=False, indent=2)
        print("Esqueleto de entrada do cálculo gravado em", calc_out)
    sys.exit(1 if r["erros"] else 0)


if __name__ == "__main__":
    main()
