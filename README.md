# dir-bank-adv — Ecossistema de apoio a escritório de advocacia bancária

Ferramentas internas para um escritório que atua **contra bancos** em ações revisionais de financiamento de veículos (juros abusivos, tarifas, seguros, mora, busca e apreensão).

> Princípio: **a IA extrai e redige; o código calcula; o advogado decide.** Tudo que sai daqui é rascunho para revisão de advogado.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `apps/revisional/` | Web app "Revisional": calculadora revisional, `schema.sql` do Supabase com RLS, testes do motor JS |
| `skills/` | 7 skills do Claude: cálculo, base jurídica, peça inicial, leitor de contrato, triagem, compliance, prazos |
| `docs/` | Arquitetura, roadmap, backlog e materiais de compliance (OAB/LGPD) |
| `.github/` | Modelos de issue/PR, CI (testes + gitleaks), Dependabot |

## Skills

`calculo-revisional-veiculos` · `legal-kb-revisional` · `peca-revisional-inicial` · `leitor-contrato-financiamento` · `triagem-caso-revisional` · `compliance-oab-lgpd` · `prazos-processuais`

Cada uma tem `SKILL.md` e scripts testados. Para empacotar (`.skill`) use o `package_skill.py` do skill-creator.

## Testes

```bash
node apps/revisional/test.js
python3 skills/calculo-revisional-veiculos/scripts/test_calc.py
python3 skills/compliance-oab-lgpd/scripts/test_pseudonimizar.py
python3 skills/prazos-processuais/scripts/test_contar_prazo.py
```

## Regras inegociáveis

1. **Nenhum dado real de cliente neste repositório** (CPF, CNPJ, placa, nº de contrato, PDFs, planilhas). Só dados sintéticos. O CI roda gitleaks com regras específicas (`gitleaks.toml`).
2. **Citações jurídicas só da base curada** (`skills/legal-kb-revisional/references/kb.yaml`) e conferidas no portal oficial. Entradas com `verificado_em` vazio são "pendentes de conferência".
3. **Nada é protocolado nem enviado ao cliente sem revisão de advogado.**
4. Segredos em GitHub Secrets ou cofre, nunca no código.

Leia `docs/ARQUITETURA.md`, `docs/ROADMAP.md` e `docs/BACKLOG.md`.
