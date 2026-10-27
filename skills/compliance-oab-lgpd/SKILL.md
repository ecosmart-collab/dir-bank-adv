---
name: compliance-oab-lgpd
description: Aplica as regras de uso de IA na advocacia (Recomendação CFOAB 001/2024), sigilo profissional e LGPD no escritório de advocacia bancária — pseudonimiza dados de clientes antes de enviá-los a modelos ou ao repositório, fornece política interna de IA, cláusula de honorários, RIPD, checklist de revisão de peça e de segurança do ambiente, regras gitleaks e .gitignore para manter dados de clientes fora do Git. Use sempre que houver CPF, nome, contrato, placa, extrato ou documento de cliente a ser enviado a uma ferramenta, ao GitHub, ao n8n ou a um LLM; ao perguntarem "posso mandar isso para a IA?", "o que a OAB exige?", "LGPD", "política de IA", "cláusula de IA", "RIPD", "vazamento"; e ao revisar uma peça ou configurar o repositório do projeto.
---

# Compliance OAB e LGPD para o escritório

## Por que esta skill é transversal

Todas as outras skills do escritório lidam com contratos, CPF, placas e dados financeiros de clientes. Dois riscos reais: (1) violar sigilo e LGPD ao mandar dados identificáveis para ferramentas de terceiros ou ao deixá-los em repositório; (2) advogados sancionados por peças com citações falsas geradas por IA. Esta skill dá o procedimento para evitar os dois, antes do problema.

## Regras de bolso (aplicar em qualquer tarefa)

1. **Antes de enviar texto de cliente a qualquer ferramenta externa ou LLM**, pseudonimizar: `python3 scripts/pseudonimizar.py entrada.txt saida.txt --mapa mapa.json --nomes "Nome do Cliente" "Nome da Contraparte"`. O mapa de reversão é dado pessoal: guardar fora do repositório, sem enviá-lo a ninguém.
2. **Nunca** colocar PDFs, contratos, planilhas de clientes, CPF, placas ou nº de contrato em arquivos do repositório, em issues, em PRs, em prompts de agentes versionados ou em workflows do n8n exportados. Usar dados sintéticos.
3. **A IA nunca decide nem protocola.** Peça, parecer, notificação e mensagem ao cliente saem só com revisão e aprovação de advogado.
4. **Citação só da legal-kb**, conferida no portal oficial (skill `legal-kb-revisional`).
5. **Transparência:** o assistente se identifica como automatizado; o cliente pode falar com humano; o uso de IA consta do contrato de honorários.
6. **Dúvida sobre enviar ou não?** Não enviar. Pseudonimizar ou perguntar ao responsável.

## O que a Recomendação CFOAB 001/2024 pede (resumo, conferir texto oficial)

Chatbots não praticam atos privativos e devem se identificar como máquina; julgamento profissional não é delegável à IA sem supervisão humana; dependência excessiva de IA é incompatível com a advocacia; o uso de IA deve ser formalizado ao cliente antes de começar; o cliente tem direito de interagir com um humano. A OAB anunciou um Código de Boas Práticas e um futuro provimento sobre IA que, até out/2026, não haviam sido publicados: acompanhar e atualizar a política quando saírem.

## O que a LGPD exige na prática

- **Bases legais** típicas: execução de contrato e exercício regular de direitos em processo (art. 7º, V e VI); dados sensíveis (ex.: saúde em seguro prestamista) só quando indispensáveis (art. 11).
- **Registro das operações de tratamento** (art. 37) e **RIPD** para o módulo de IA (art. 38) — modelo em `references/ripd_modelo.md`.
- **Encarregado** indicado e canal para titulares.
- **Transferência internacional** (art. 33): enviar dados a LLM ou nuvem fora do país exige salvaguardas; preferir provedores sem treino com os dados e retenção mínima.
- **Incidentes** (art. 48): plano de contenção e comunicação à ANPD e aos titulares quando aplicável.
- A ANPD incluiu IA entre seus focos de fiscalização de 2026-2027.

## Mapa dos materiais

| Preciso de… | Arquivo |
|---|---|
| Política interna de uso de IA | `references/politica_uso_ia.md` |
| Cláusula e termo de ciência para o contrato de honorários | `references/clausula_honorarios_ia.md` |
| Relatório de impacto (RIPD) | `references/ripd_modelo.md` |
| Checklist antes de protocolar peça | `references/checklist_revisao_peca.md` |
| Checklist de segurança (Supabase, GitHub, IA, operação) | `references/checklist_seguranca_sistema.md` |
| Regras gitleaks, .gitignore e pre-commit para o repositório | `references/repo_seguranca/` |
| Pseudonimizar/reverter texto | `scripts/pseudonimizar.py` (teste: `scripts/test_pseudonimizar.py`) |

## Como atuar em situações comuns

- **"Posso colar o contrato do cliente aqui?"** Preferir o texto pseudonimizado. Se o contrato é necessário em PDF para leitura, usar apenas ferramentas da lista aprovada e anotar o uso. Lembrar que a extração só precisa de taxas, valores e datas, não de identificação.
- **Configurando o repositório:** entregar `gitleaks.toml`, `gitignore_clientes.txt` e `pre-commit-config.yaml`, e percorrer o checklist de segurança. Reforçar: dados reais jamais no Git; fixtures sintéticas em `tests/golden`.
- **Revisando peça:** conduzir o `checklist_revisao_peca.md` com o advogado e registrar o uso de IA.
- **Incidente (dado de cliente enviado ou commitado por engano):** parar, não repetir o envio, avisar o responsável no mesmo dia; se foi para o Git, não basta apagar o arquivo (o histórico guarda): tratar como incidente, rotacionar segredos e reescrever o histórico com apoio técnico. Avaliar a comunicação à ANPD e aos titulares.

## Limites

Os modelos são ponto de partida e precisam de validação pelo responsável do escritório (ou consultoria de proteção de dados). Não substituem parecer jurídico sobre a LGPD nem a leitura dos atos oficiais da OAB e da ANPD, que mudam com frequência. O pseudonimizador é rede de segurança por padrões: nomes só são detectados se informados em `--nomes`, e a saída deve ser revisada antes do envio.
