# Arquitetura

## Fluxo do caso

```
Cliente/WhatsApp → triagem-caso-revisional → leitor-contrato-financiamento
      → (conferência humana dos campos críticos) → calculo-revisional-veiculos
      → peca-revisional-inicial (+ legal-kb-revisional valida citações)
      → revisão do advogado → protocolo (humano)
prazos-processuais acompanha o processo depois do protocolo.
compliance-oab-lgpd atravessa todas as etapas (pseudonimização, políticas, repositório).
```

## Componentes

- **Motor de cálculo determinístico** (`skills/calculo-revisional-veiculos/scripts/calc_revisional.py` e `apps/revisional/calc.js`): Tabela Price, taxa implícita por bisseção, parcela revisada com taxa de referência BACEN (SGS 25471 a.m. / 20749 a.a.), indébito corrigido e juros. Versionado (`CALC_VERSION`) e com hash da entrada para reprodutibilidade.
- **Base jurídica curada** (`kb.yaml`): única fonte de citações; validador (`validar_citacoes.py`) falha se a peça citar algo fora dela.
- **Montador de peça** (`montar_peca.py`): módulos em `assets/modulos`, campos pendentes explícitos, relatório JSON.
- **App web + Supabase** (`apps/revisional`): RLS por escritório/caso, auditoria append-only (ver `docs/compliance/checklist_seguranca_sistema.md`).

## Decisões

| Decisão | Motivo |
|---|---|
| LLM só extrai/redige; cálculo em código | Reprodutibilidade e auditoria; evita erro numérico |
| Citação só da KB | Evita jurisprudência inventada (risco disciplinar) |
| Pseudonimização antes de enviar a LLM | Sigilo profissional e LGPD |
| Monorepo | Skills, app e docs evoluem juntos; um CI |

## Pontos jurídicos em aberto (reconferir)

Tema 1.378/STJ (juros abusivos, sem tese fixada até out/2026 segundo a pesquisa); a regra "1,5x a média" não é tese vinculante; modulação do dobro (30/3/2021); busca e apreensão extrajudicial (Lei 14.711/2023, ADIs 7600/7601/7608). Toda tese deve ser conferida no portal oficial antes do uso.
