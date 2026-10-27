# Metodologia do cálculo revisional

## Fórmulas (Tabela Price)

- Parcela: `PMT = PV · i / (1 − (1+i)^−n)`
- Taxa efetiva mensal: resolve `PMT(valor, i, n) = parcela cobrada` por bisseção (200 iterações).
- Taxa anual efetiva: `(1+i)^12 − 1`.
- Parcela revisada: `PMT(valor − encargos excluídos, taxa de referência, n)`.
- Diferença por parcela: `cobrada − revisada`.
- Saldo devedor das parcelas restantes: valor presente das parcelas a vencer (contratual à taxa efetiva; revisado à taxa de referência).

## Atualização do indébito

Para cada parcela paga, do mês seguinte ao do pagamento até o mês da data-base:

1. Correção: fator composto `Π(1 + indice_mensal)` com o índice do regime vigente em cada mês.
2. Juros: soma das taxas mensais do regime de cada mês, aplicada como juros **simples** sobre o valor corrigido.
3. Repetição: multiplicador 2 para pagamentos em/após `dobro_a_partir_de` (padrão 30/3/2021) ou sempre, se `ma_fe_antes`.

A convenção (correção composta + juros simples sobre o corrigido) é uma escolha de modelagem. Se o título judicial ou a tabela do tribunal fixar outra convenção (por exemplo, juros desde a citação, ou a partir do evento danoso), adaptar o cálculo e registrar a divergência no laudo.

## Regimes por período

Cada item de `regimes` vale a partir de `inicio` até o início do próximo.

| Período | Referência | Observação |
|---|---|---|
| Até 29/8/2024 | Índice do título ou tabela do tribunal; juros conforme o título | Conferir o que o juízo determinou |
| A partir de 30/8/2024 | IPCA (art. 389, parágrafo único, CC) + taxa legal (art. 406, §1º, CC) | Lei 14.905/2024; taxa legal divulgada pelo BCB (conferir valor e série no SGS) |

Os valores de exemplo em `exemplo_entrada.json` são ilustrativos. Antes de usar em caso real, substituir pelos valores oficiais.

## Taxa de referência (BACEN)

- SGS **25471**: taxa média mensal, aquisição de veículos, pessoa física, recursos livres (% a.m.).
- SGS **20749**: a mesma taxa em % a.a.
- Comparar na mesma unidade e na competência do mês da contratação.
- As séries podem ser revisadas pelo BCB. Guardar o valor bruto retornado e a data da consulta.
- A API limita o volume por consulta: sempre informar `dataInicial` e `dataFinal`.
- Os códigos e valores devem ser conferidos no SGS antes de uso processual.

## O que fica de fora

SAC, carência, amortização extraordinária, renegociação, juros pós-fixados e contratos com IOF/CET detalhados por parcela. Nesses casos, usar perícia ou cálculo específico.
