# Roadmap

| Fase | Objetivo | Entregas |
|---|---|---|
| 0 — Fundação (feito) | Motor de cálculo, app, 7 skills, compliance | Este repositório |
| 1 — Verificação | Tornar a base jurídica confiável | Conferir cada entrada da KB nos portais (STF/STJ/Planalto), preencher `verificado_em`; golden tests com contratos sintéticos; conferir motor com perito/contador |
| 2 — Piloto | Usar em casos reais com segurança | Supabase real com RLS testada, MFA, auditoria; RIPD e política de IA aprovadas; piloto com 5–10 casos reais pseudonimizados |
| 3 — Automação | Reduzir trabalho operacional | Entrada do cliente (WhatsApp/formulário), n8n sem credenciais exportadas, agenda de prazos com alertas, painel de carteira |
| 4 — Expansão | Outras teses/nichos | Revisional de outros contratos bancários, tributário, jurimetria |

## Critérios para sair do piloto

- 100% das citações da KB conferidas e datadas.
- Motor conferido por responsável técnico em amostra de contratos.
- Nenhum achado do gitleaks; RLS testada com papéis distintos.
