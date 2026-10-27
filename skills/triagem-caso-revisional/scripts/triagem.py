#!/usr/bin/env python3
"""Classifica a urgência de um novo caso de financiamento de veículo e lista documentos faltantes.

Uso:  python3 triagem.py intake.json [saida.json]

intake.json (use PSEUDÔNIMO do cliente; sem CPF/endereço):
{
  "cliente_ref": "C-0123",
  "banco": "Banco Exemplo",
  "data_contratacao": "2022-05-10",
  "situacao": {
    "parcelas_atrasadas": 2, "notificacao_recebida": false, "negativado": false,
    "liminar_busca_apreensao": false, "veiculo_apreendido": false, "leilao_marcado": false,
    "acao_judicial_em_curso": false, "prazo_processual_em_curso": false, "procedimento_extrajudicial": false
  },
  "teses_candidatas": ["juros", "tarifas"],
  "documentos_disponiveis": ["contrato_completo", "comprovantes_pagamento"]
}

A triagem é um apoio: a classificação de urgência e o encaminhamento SEMPRE passam por um humano.
Em urgência CRITICA ou ALTA o caso vai para advogado no mesmo dia.
"""
import json
import sys

DOCS_BASE = {
    "contrato_completo": "Contrato/CCB completo, todas as páginas, incluindo quadro-resumo e anexos",
    "documento_identidade_cpf": "RG/CNH e CPF do cliente",
    "comprovante_residencia": "Comprovante de residência atual",
    "crlv": "CRLV do veículo (verificar gravame)",
    "comprovantes_pagamento": "Comprovantes ou extrato dos pagamentos das parcelas",
    "comprovante_renda": "Comprovante de renda (para gratuidade da justiça)",
}
DOCS_POR_TESE = {
    "juros": {"demonstrativo_credito": "Demonstrativo de crédito/CET e planilha de evolução, se houver"},
    "capitalizacao": {},  # depende do contrato completo (cláusulas de juros)
    "tarifas": {
        "demonstrativo_credito": "Demonstrativo de crédito com discriminação das tarifas",
        "comprovante_registro": "Comprovante de registro do contrato/gravame no órgão de trânsito, se o cliente tiver",
    },
    "seguro": {"proposta_apolice_seguro": "Proposta, termo de adesão e/ou apólice do seguro"},
    "comissao_permanencia": {"extrato_atraso": "Extrato de atraso/boletos com encargos de inadimplência"},
    "mora_busca_apreensao": {
        "notificacao_extrajudicial": "Notificação extrajudicial (carta/AR) recebida, com envelope se houver",
        "decisao_mandado": "Decisão liminar, mandado ou comunicado de busca e apreensão",
    },
    "negativacao": {"extrato_negativacao": "Extrato de restrição (SPC/Serasa/outros)"},
}
ORDEM = ["CRITICA", "ALTA", "MEDIA", "BAIXA"]


def classificar(intake):
    s = intake.get("situacao", {})
    motivos = {"CRITICA": [], "ALTA": [], "MEDIA": [], "BAIXA": []}
    if s.get("veiculo_apreendido"):
        motivos["CRITICA"].append("Veículo já apreendido: há prazo curto para purgar a mora/pagar a dívida integral (Tema 722; Lei 14.711/2023, art. 8º-C §9º do DL 911/69). Advogado confere o prazo exato e a via (judicial ou extrajudicial).")
    if s.get("liminar_busca_apreensao"):
        motivos["CRITICA"].append("Liminar de busca e apreensão deferida: risco imediato de perda do veículo.")
    if s.get("leilao_marcado"):
        motivos["CRITICA"].append("Leilão marcado: prazo em curso.")
    if s.get("prazo_processual_em_curso"):
        motivos["CRITICA"].append("Ação judicial com prazo processual em curso (citação/intimação): conferir o prazo hoje.")
    if s.get("procedimento_extrajudicial"):
        motivos["CRITICA"].append("Procedimento extrajudicial de consolidação/busca e apreensão (Lei 14.711/2023) em andamento: prazos próprios, verificar hoje.")
    if s.get("notificacao_recebida"):
        motivos["ALTA"].append("Notificação extrajudicial recebida: mora em formalização e prazo para regularizar (Súmula 72/STJ; Tema 1.132).")
    if (s.get("parcelas_atrasadas") or 0) >= 3:
        motivos["ALTA"].append(f"{s['parcelas_atrasadas']} parcelas em atraso: risco crescente de notificação e busca e apreensão.")
    if s.get("negativado"):
        motivos["ALTA"].append("Nome negativado por este contrato.")
    if 1 <= (s.get("parcelas_atrasadas") or 0) <= 2:
        motivos["MEDIA"].append(f"{s['parcelas_atrasadas']} parcela(s) em atraso.")
    if s.get("acao_judicial_em_curso") and not s.get("prazo_processual_em_curso"):
        motivos["MEDIA"].append("Há ação judicial em curso sem prazo imediato informado: confirmar fase e próximos prazos.")
    nivel = next((n for n in ORDEM if motivos[n]), "BAIXA")
    if nivel == "BAIXA":
        motivos["BAIXA"].append("Contrato em dia e sem medida de cobrança informada.")
    return nivel, motivos


def documentos(intake):
    tem = set(intake.get("documentos_disponiveis", []))
    teses = list(intake.get("teses_candidatas", []))
    s = intake.get("situacao", {})
    if s.get("notificacao_recebida") or s.get("liminar_busca_apreensao") or s.get("veiculo_apreendido") or s.get("procedimento_extrajudicial"):
        teses.append("mora_busca_apreensao")
    if s.get("negativado"):
        teses.append("negativacao")
    precisa = dict(DOCS_BASE)
    for t in teses:
        precisa.update(DOCS_POR_TESE.get(t, {}))
    faltam = [{"codigo": k, "descricao": v} for k, v in precisa.items() if k not in tem]
    return faltam, teses


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    with open(sys.argv[1], encoding="utf-8") as f:
        intake = json.load(f)
    nivel, motivos = classificar(intake)
    faltam, teses = documentos(intake)
    encaminhamento = {
        "CRITICA": "Advogado responsável HOJE (imediato). Não aguardar documentos para acionar.",
        "ALTA": "Advogado no mesmo dia útil.",
        "MEDIA": "Análise do advogado em até 2 dias úteis.",
        "BAIXA": "Fila normal de análise de viabilidade.",
    }[nivel]
    saida = {
        "cliente_ref": intake.get("cliente_ref"),
        "urgencia": nivel,
        "motivos": motivos[nivel] + [m for n in ORDEM if n != nivel for m in motivos[n]],
        "encaminhamento": encaminhamento,
        "teses_candidatas": sorted(set(teses)),
        "documentos_faltantes": faltam,
        "aviso": "Classificação de apoio. A decisão de urgência e a orientação ao cliente são do advogado.",
    }
    out = json.dumps(saida, ensure_ascii=False, indent=2)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(out)
    print(out)


if __name__ == "__main__":
    main()
