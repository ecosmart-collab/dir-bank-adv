---
name: triagem-caso-revisional
description: Faz a triagem de novos clientes de financiamento de veículo no escritório de advocacia bancária — perguntas de intake, classificação de urgência (busca e apreensão, notificação, atraso, negativação, leilão, prazo em curso), checklist de documentos por tese (juros, tarifas, seguro, mora) e mensagens ao cliente no padrão OAB, com transbordo para advogado. Use sempre que chegar um cliente novo, lead de WhatsApp ou site, pedido de "triar", "organizar documentos do cliente", "o que falta pedir", "esse caso é urgente?", "montar o fluxo de atendimento" ou "agente de triagem", mesmo que o usuário não cite a skill.
---

# Triagem de casos revisionais

## Objetivo

Em um escritório com muitos clientes de financiamento de veículo, o gargalo é o início: descobrir rápido **o que é urgente** (para ninguém perder o carro por falta de prazo) e **o que falta** para o advogado decidir se há tese. A skill padroniza a coleta, classifica a urgência por regras explícitas e produz a lista de pendências documentais. A decisão é sempre humana: a triagem apenas organiza e prioriza.

## Fluxo

1. **Atender ou receber o intake.** Se o cliente está em conversa, seguir `references/mensagens_cliente.md` (abertura identificando que é assistente automatizado, perguntas na ordem, regras de atendimento). Se o intake já veio preenchido (formulário, n8n, equipe), partir dele.
2. **Registrar sem dados pessoais desnecessários.** Usar um código de cliente (`cliente_ref`) no JSON de triagem. Nome, CPF e endereço ficam no sistema de casos com controle de acesso, não em arquivos soltos.
3. **Classificar:** montar `intake.json` (modelo no cabeçalho de `scripts/triagem.py`) e rodar `python3 scripts/triagem.py intake.json saida.json`. A saída traz `urgencia`, `motivos`, `encaminhamento`, teses candidatas e `documentos_faltantes`.
4. **Agir conforme a urgência:**
   - **CRÍTICA** (veículo apreendido, liminar, leilão, prazo processual ou procedimento extrajudicial em curso): acionar o advogado responsável imediatamente, antes de coletar documentos. Avisar o cliente de que um advogado entrará em contato com prioridade, sem prometer resultado nem orientar sobre pagar ou não pagar.
   - **ALTA** (notificação recebida, 3+ parcelas em atraso, negativação): advogado no mesmo dia útil.
   - **MÉDIA** (1 a 2 parcelas em atraso, ação em curso sem prazo imediato): análise em até 2 dias úteis.
   - **BAIXA:** fila normal de viabilidade.
5. **Pedir documentos** com a lista gerada (`references/checklists.md` explica por que cada um importa). Receber somente pelo canal seguro do escritório.
6. **Encaminhar ao fluxo seguinte:** contrato completo recebido segue para `leitor-contrato-financiamento`; depois, cálculo (`calculo-revisional-veiculos`) e parecer de viabilidade pelo advogado.

## Por que cada gatilho de urgência

- **Apreensão, liminar, mandado:** a purga da mora exige pagar a dívida integral em prazo curto após a apreensão (Tema 722/STJ; Lei 14.711/2023). O prazo depende da via (judicial ou extrajudicial) e quem confere é o advogado.
- **Notificação recebida:** é o passo que formaliza a mora (Súmula 72/STJ); basta o envio ao endereço do contrato (Tema 1.132/STJ). Quanto antes o advogado souber, mais opções existem.
- **Procedimento extrajudicial (Lei 14.711/2023):** o STF validou a busca e apreensão extrajudicial; os prazos são próprios e o devedor tem menos formalidades a explorar.
- **Atraso crescente e negativação:** aumentam o risco e influenciam o pedido de tutela.

## Regras de atendimento (resumo)

Identificar-se como assistente; não dar orientação jurídica ("posso parar de pagar?", "vou ganhar?" vão para advogado); garantir acesso a humano; informar o uso de IA; pedir só o necessário. Detalhes e textos prontos em `references/mensagens_cliente.md`.

## Limites

Cobre financiamento de veículo. Para imóvel, consignado, cartão ou empréstimo pessoal, os gatilhos e checklists mudam. Se o cliente descrever situação de violência, risco de vida ou outro tema fora do escopo, encerrar a triagem e acionar um humano.
