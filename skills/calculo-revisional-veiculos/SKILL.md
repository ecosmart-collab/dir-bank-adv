---
name: calculo-revisional-veiculos
description: Calcula e apresenta a revisão de contratos de financiamento de veículos (Tabela Price) para o escritório de advocacia bancária — taxa efetiva cobrada, comparação com a taxa média do BACEN, exclusão de encargos financiados, indébito parcela a parcela (simples antes de 30/3/2021, em dobro depois), saldo devedor revisado e laudo/demonstrativo. Use sempre que o usuário falar em revisional, juros abusivos, recálculo de financiamento, taxa efetiva, indébito, repetição em dobro, laudo de cálculo, "calcular o contrato do cliente", CCB ou CDC de veículo, mesmo que não peça "a calculadora" explicitamente.
---

# Cálculo revisional de financiamento de veículos

Esta skill orienta o uso do motor de cálculo `scripts/calc_revisional.py` e a apresentação do resultado. O motor é determinístico e versionado; o papel do Claude é montar a entrada corretamente, rodar o motor, **conferir** o resultado e explicá-lo ao advogado. O Claude não improvisa contas de cabeça: todo número do laudo vem do script.

Por que isso importa: o laudo pode ser impugnado ou periciado meses depois. Só um cálculo reproduzível (mesma entrada, mesma versão, mesmo resultado) resiste a isso.

## Fluxo

1. **Reunir a entrada.** Se o contrato já foi lido pela skill `leitor-contrato-financiamento`, usar o JSON validado dela. Caso contrário, pedir ao usuário o mínimo: valor financiado, nº de parcelas, taxa mensal (e anual, se constar), valor da parcela cobrada, data de contratação, primeiro vencimento, encargos financiados (TAC, tarifas, registro, avaliação, seguro) e quantas parcelas foram pagas (ou as datas reais dos pagamentos).
2. **Obter a taxa de referência.** Série SGS 25471 (% a.m.) ou 20749 (% a.a.), da **competência do mês da contratação**. Registrar série, competência, data da consulta e o valor bruto exato. Se o usuário não informou o valor e há acesso à rede, consultar `https://api.bcb.gov.br/dados/serie/bcdata.sgs.25471/dados?formato=json&dataInicial=dd/mm/aaaa&dataFinal=dd/mm/aaaa` (sempre com intervalo de datas). Sem acesso, pedir o valor ao usuário. Nunca inventar nem aproximar a taxa. Ver `references/metodologia.md`.
3. **Definir os regimes de correção e juros** (lista `regimes` no JSON): índice e juros por período, conforme o título judicial ou a tabela do tribunal. Para atualização sem título, o regime supletivo a partir de 30/8/2024 é IPCA + taxa legal (Lei 14.905/2024); antes disso depende do índice adotado pelo juízo. Se o usuário não souber, deixar o campo e avisar que os valores "corrigidos" são provisórios.
4. **Rodar o motor:** `python3 scripts/calc_revisional.py entrada.json saida.json`. Usar `scripts/exemplo_entrada.json` como molde.
5. **Conferir antes de apresentar.** Verificar se a parcela cobrada bate com a parcela pela taxa informada, se a data-base está correta e se há alertas (`alertas` na saída). Resolver ou comunicar cada alerta.
6. **Apresentar** no formato abaixo. Se o advogado quiser arquivo, gerar planilha (skill `xlsx`) ou Word (skill `docx`) a partir do JSON de saída, nunca recalculando à mão.

## Regras que o motor aplica (e que o Claude deve respeitar na explicação)

- **Dobro só a partir de 30/3/2021.** Pagamentos anteriores são devolvidos de forma simples (modulação do EAREsp 676.608/RS), salvo prova de má-fé (`ma_fe_antes`). O resumo traz as duas parcelas separadas; mostre as duas.
- **Múltiplo da taxa média é alerta, não veredito.** O limiar padrão de 1,5x é configurável (`multiplo_alerta`). A taxa média sozinha não prova abusividade, e o Tema 1.378/STJ está pendente de julgamento. Ao comentar o resultado, sugerir ao advogado registrar fundamentos adicionais (custo de captação, spread, risco, garantia, idade do veículo). Não escrever "juros abusivos" como conclusão.
- **Teste do duodécuplo** (Súmula 541/STJ): taxa anual maior que 12x a mensal indica capitalização pactuada. Sem taxa anual no contrato, o alerta pede conferência da cláusula (Súmula 539/STJ; Tema 953).
- **Encargos financiados** são retirados do principal na revisão. Cada um depende de prova (tarifa sem serviço prestado, seguro sem opção de escolha, etc.): listar quais foram excluídos e deixar a decisão com o advogado.
- **Prescrição:** o motor sinaliza pagamentos com mais de 10 anos da data-base. O termo inicial é controverso; repassar o alerta tal como está.
- **Limites:** só Tabela Price (parcelas iguais). Para SAC, carência, amortizações extraordinárias ou renegociações, avisar que o motor não cobre e recomendar perícia ou cálculo específico.

## Formato da resposta ao advogado

Resumo curto, nesta ordem:

1. **Taxa efetiva** (mensal e anual) × **taxa contratada** × **taxa de referência** (com série e competência) e a razão entre efetiva e referência.
2. **Parcela cobrada × parcela revisada** e a diferença por parcela.
3. **Indébito**: total simples, parcela devida em dobro (pós 30/3/2021), total apurado, mais correção e juros.
4. **Saldo devedor** contratual × revisado.
5. **Alertas** do motor, com a ação sugerida para cada um.
6. **Rodapé de reprodutibilidade:** `calc_version`, `regras_versao`, série BACEN e competência, data-base e `entrada_sha256`.

Fechar sempre com a ressalva: cálculo de apoio, sujeito à conferência do advogado e, se houver impugnação, à perícia contábil.

## O que esta skill não faz

Não decide a tese, não afirma abusividade, não cita jurisprudência por conta própria (usar a skill `legal-kb-revisional`) e não redige a petição (usar `peca-revisional-inicial`). Dados de clientes reais não vão para arquivos do repositório: usar a skill `compliance-oab-lgpd` para pseudonimizar antes de compartilhar.

## Testes

`python3 scripts/test_calc.py` valida o motor (PMT, taxa implícita, modulação do dobro, alertas). Rodar após qualquer alteração e subir a versão em `CALC_VERSION` quando o resultado de algum cálculo mudar.
