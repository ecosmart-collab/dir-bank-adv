#!/usr/bin/env python3
"""Contador de prazos processuais CÍVEIS (CPC) — conservador, auditável.

Uso:
  contar_prazo.py entrada.json [--saida resultado.json]

entrada.json:
{
  "evento": "2026-03-10",              # data da disponibilização (dje) ou da ciência (direto)
  "modo": "dje" | "direto",            # dje: art. 224 §§2-3 CPC; direto: intimação/citação cuja data de ciência já é conhecida
  "prazo": 15,                         # nº de dias
  "tipo": "uteis" | "corridos",        # CPC art. 219: úteis (padrão). Corridos só se a lei especial mandar.
  "multiplicador": 1,                  # 2 = prazo em dobro (ex.: Defensoria/Fazenda — conferir lei aplicável)
  "feriados": ["2026-04-03", ...],     # OBRIGATÓRIO: feriados e dias sem expediente forense da comarca/tribunal
  "suspensao": [["2026-12-20","2027-01-20"]],  # padrão: 20/12 a 20/01 (CPC art. 220). Informe outras (ex.: indisponibilidade do sistema)
  "descricao": "Contestação"
}
Saída: vencimento (prazo FATAL), data-alvo interna (2 dias úteis antes) e avisos. NUNCA é a palavra final:
o advogado confere o resultado no calendário forense do tribunal antes de depender dele.
"""
import json, sys
from datetime import date, timedelta

VERSAO = "1.0.0"
FOLGA_INTERNA_DIAS_UTEIS = 2


def d(s):
    return date.fromisoformat(s)


def suspenso(dia, suspensoes):
    return any(a <= dia <= b for a, b in suspensoes)


def util(dia, feriados, suspensoes):
    return dia.weekday() < 5 and dia not in feriados and not suspenso(dia, suspensoes)


def proximo_util(dia, feriados, suspensoes, limite=400):
    n = 0
    while not util(dia, feriados, suspensoes):
        dia += timedelta(days=1)
        n += 1
        if n > limite:
            raise ValueError("Não encontrou dia útil: confira feriados/suspensões.")
    return dia


def padrao_suspensao(ano_ini, ano_fim):
    # CPC art. 220: suspende de 20/12 a 20/01, inclusive.
    return [(date(a, 12, 20), date(a + 1, 1, 20)) for a in range(ano_ini - 1, ano_fim + 1)]


def contar(ent):
    avisos = []
    evento = d(ent["evento"])
    modo = ent.get("modo", "dje")
    prazo = int(ent["prazo"])
    tipo = ent.get("tipo", "uteis")
    mult = int(ent.get("multiplicador", 1))
    feriados = {d(x) for x in ent.get("feriados", [])}
    if "suspensao" in ent:
        suspensoes = [(d(a), d(b)) for a, b in ent["suspensao"]]
    else:
        suspensoes = padrao_suspensao(evento.year, evento.year + 2)
        avisos.append("SUSPENSAO_PADRAO: aplicada a suspensão de 20/12 a 20/01 (CPC art. 220). Confirme se vale para este prazo/tribunal.")
    if tipo == "uteis" and not feriados:
        avisos.append("SEM_FERIADOS: nenhum feriado informado. O resultado ignora feriados e dias sem expediente: NÃO use sem conferir o calendário do tribunal.")
    if tipo == "corridos":
        avisos.append("CORRIDOS: confirme que a lei especial determina contagem em dias corridos (CPC, art. 219, usa dias úteis).")
    total = prazo * mult
    if mult != 1:
        avisos.append(f"DOBRO: multiplicador {mult} aplicado; confirme o fundamento legal e se há exceção (ex.: prazo próprio, processo eletrônico, art. 229 §2º).")

    if modo == "dje":
        # disponibilização no DJe; publicação = primeiro dia útil seguinte (CPC art. 224 §2º)
        publicacao = proximo_util(evento + timedelta(days=1), feriados, suspensoes)
        base = publicacao
        avisos.append(f"DJE: disponibilizado em {evento}, considerado publicado em {publicacao} (art. 224 §2º).")
    elif modo == "direto":
        base = evento
    else:
        raise ValueError("modo deve ser 'dje' ou 'direto'")

    # exclui o dia do começo; início da contagem no primeiro dia útil seguinte (art. 224 §3º)
    cursor = base + timedelta(days=1)
    inicio = proximo_util(cursor, feriados, suspensoes)
    dia = inicio - timedelta(days=1)
    contados = 0
    dias_marcados = []
    while contados < total:
        dia += timedelta(days=1)
        if tipo == "uteis":
            if util(dia, feriados, suspensoes):
                contados += 1
                dias_marcados.append(dia)
        else:
            if not suspenso(dia, suspensoes):
                contados += 1
                dias_marcados.append(dia)
    vencimento = dia
    if tipo == "corridos":
        # prazo que termina em dia sem expediente prorroga ao primeiro dia útil (art. 224 §1º)
        v2 = proximo_util(vencimento, feriados, suspensoes)
        if v2 != vencimento:
            avisos.append(f"PRORROGACAO: vencimento caía em dia sem expediente; prorrogado para {v2} (art. 224 §1º).")
            vencimento = v2
    # data-alvo interna
    alvo = vencimento
    folga = 0
    while folga < FOLGA_INTERNA_DIAS_UTEIS:
        alvo -= timedelta(days=1)
        if util(alvo, feriados, suspensoes):
            folga += 1
    if alvo <= base:
        alvo = base
        avisos.append("ALVO_INTERNO_CURTO: o prazo é tão curto que a data-alvo interna coincide com o início.")
    return {
        "versao_contador": VERSAO,
        "descricao": ent.get("descricao", ""),
        "evento": evento.isoformat(),
        "modo": modo,
        "base_contagem": base.isoformat(),
        "primeiro_dia_contado": dias_marcados[0].isoformat() if dias_marcados else None,
        "prazo_dias": total,
        "tipo": tipo,
        "vencimento_fatal": vencimento.isoformat(),
        "vencimento_dia_semana": ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"][vencimento.weekday()],
        "data_alvo_interna": alvo.isoformat(),
        "avisos": avisos,
        "conferencia_obrigatoria": "Conferir no calendário do tribunal/comarca e nos autos (data efetiva da intimação) por advogado. Feriado local, se invocado em recurso, deve ser comprovado no ato de interposição (CPC art. 1.003, §6º — conferir).",
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ent = json.load(open(argv[1], encoding="utf-8"))
    res = contar(ent)
    txt = json.dumps(res, ensure_ascii=False, indent=2)
    if "--saida" in argv:
        open(argv[argv.index("--saida") + 1], "w", encoding="utf-8").write(txt)
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
