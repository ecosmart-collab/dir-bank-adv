---
name: legal-kb-revisional
description: Base curada de súmulas, temas repetitivos, precedentes e normas para o escritório de advocacia bancária (revisional de financiamento de veículos, juros, capitalização, tarifas, seguro, comissão de permanência, mora, busca e apreensão, repetição em dobro, prescrição), com status consolidado ou controverso e fonte oficial. É a ÚNICA fonte permitida para citações jurídicas em peças e pareceres. Use sempre que for citar, conferir ou resumir súmula, tema, REsp ou lei em contexto bancário, ao revisar um rascunho de petição, ao responder "qual o entendimento do STJ sobre…" ou "isso ainda vale?", e antes de qualquer texto jurídico sair do escritório — mesmo que o usuário não peça a base explicitamente.
---

# Base jurídica curada (legal-kb)

## Por que esta skill existe

Tribunais já multaram advogados por citar jurisprudência inexistente gerada por IA, e o entendimento sobre juros remuneratórios está em movimento (Tema 1.378/STJ ainda sem tese em out/2026). A regra do escritório, portanto, é simples: **nenhuma citação jurídica sai do Claude se não estiver em `references/kb.yaml`**, e cada citação carrega o status do entendimento e a situação da conferência.

O Claude não confia na própria memória para jurisprudência. Se a pergunta exige algo que não está na base, diz isso e propõe incluir a entrada após conferência humana.

## Como usar

### Ao responder uma pergunta jurídica ou citar um precedente

1. Ler `references/kb.yaml` (ou filtrar por `aplica_a`: `juros`, `capitalizacao`, `tarifas`, `seguro`, `comissao_permanencia`, `mora`, `busca_apreensao`, `dobro`, `prescricao`, `atualizacao`, `inicial`, `superendividamento`).
2. Citar usando `titulo`, `numeros` e `tese` da entrada, **sem acrescentar** conteúdo que não esteja nela.
3. Informar o `status`:
   - `consolidado`: pode ser usado com a ressalva padrão de conferência;
   - `controverso` ou `pendente`: dizer expressamente que há divergência ou julgamento em curso (hoje, o Tema 1.378);
   - `mudou`: explicar o que mudou e a data;
   - `superado`: não usar como fundamento.
4. Informar a **situação da conferência**: se `verificado_em` está vazio, escrever "pendente de conferência no portal oficial" e restringir o uso a rascunho.

### Ao revisar um rascunho de peça

Rodar o validador:

```bash
python3 scripts/validar_citacoes.py rascunho.md
```

Saída `[FORA DA BASE]` significa que a citação não está curada: remover do texto, ou pedir ao advogado que confira no portal oficial para incluí-la. Código de saída 1 bloqueia o envio da peça para revisão final. Avisos de status e de conferência devem ser repassados ao advogado.

### Ao incluir ou atualizar uma entrada (somente quando o advogado confirmar)

1. Conferir no portal oficial (STJ, STF, Planalto) e copiar a fonte (URL oficial quando houver).
2. Escrever `tese` em linguagem própria e fiel, sem inventar numeração.
3. Preencher `verificado_em` (AAAA-MM-DD) e `verificado_por` (nome do advogado). Sem esses dois campos a entrada continua "pendente de conferência".
4. Atualizar `kb_versao` em `meta` (formato `kb-AAAA-MM-DD`). Esse valor entra em `regras_versao` dos cálculos.
5. Rodar `python3 scripts/validar_citacoes.py` sobre um texto de teste para garantir que o YAML continua válido.

### Quando algo mudar (ex.: o Tema 1.378 for julgado)

Atualizar a entrada, registrar a mudança em `observacao`, e avisar o advogado de que rascunhos e peças em curso que dependiam da tese anterior devem ser revisados. Cálculos anteriores continuam reproduzíveis porque guardam a `regras_versao` usada.

## Pontos de atenção que o Claude deve lembrar sempre

- A **"régua de 1,5x a média"** não é tese vinculante. Nunca escrever que ela "configura abusividade". A taxa média é referência comparativa; precedentes recentes pedem análise do caso concreto.
- A **repetição em dobro** tem modulação: cobranças a partir de 30/3/2021.
- A **propositura da revisional não afasta a mora** por si só (Súmula 380), e a abusividade de encargos acessórios também não (Tema 972). Reconhecida a abusividade dos encargos da normalidade (juros remuneratórios, capitalização), a mora é descaracterizada (REsp 1.061.530/RS).
- Súmula 284/STJ está **superada** na prática para contratos sob a Lei 10.931/2004. Não citar.
- Tarifas e seguros dependem de **prova** (serviço prestado, opção de escolha, documento apartado). A tese sozinha não basta.

## Limites

Esta skill não substitui o advogado nem emite parecer. A base foi montada a partir de relatório de pesquisa e fontes secundárias; toda entrada nasce "pendente de conferência" até alguém confirmar no portal oficial. Entendimentos fora do escopo bancário-veicular (tributário, por exemplo) ainda não estão cobertos: criar entradas novas seguindo o mesmo formato, em arquivo separado se o volume crescer.
