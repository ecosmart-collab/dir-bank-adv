---
name: peca-revisional-inicial
description: Monta o RASCUNHO da petição inicial de ação revisional de financiamento de veículo c/c repetição de indébito e tutela de urgência, com quadro de obrigações controvertidas e valor incontroverso (CPC, art. 330, §§2º e 3º), números vindos do cálculo e citações restritas à base legal-kb. Use sempre que o usuário pedir inicial, petição, peça, minuta, "redigir a revisional", "montar a ação do cliente", pedido de tutela ou depósito do incontroverso em caso de financiamento de veículo, mesmo que não cite a skill. A saída é sempre rascunho para revisão e assinatura do advogado, nunca peça final.
---

# Petição inicial revisional (rascunho)

## Por que o fluxo é assim

Uma inicial revisional falha por três motivos: inépcia por não quantificar o incontroverso (CPC, art. 330, §2º), números digitados à mão que não batem com o laudo, e citações de jurisprudência que não existem ou mudaram. Esta skill ataca os três: os valores vêm do motor de cálculo, o texto jurídico usa só módulos revisados e citações da base curada, e qualquer lacuna fica visível como `[[PREENCHER: ...]]` em vez de ser preenchida por suposição.

A peça é do advogado. O Claude monta, sinaliza e explica; quem decide as teses, os fatos e o pedido de tutela é o advogado, e quem assina é ele (Recomendação CFOAB 001/2024).

## Fluxo

1. **Pré-requisitos.** Ter o cálculo do caso (skill `calculo-revisional-veiculos`, arquivo `calculo_saida.json`) e os dados do contrato (idealmente do `leitor-contrato-financiamento`, já conferidos por humano). Sem cálculo, parar e pedir: não há como cumprir o art. 330, §2º.
2. **Escolher as teses com o advogado.** Perguntar quais se aplicam: `juros`, `capitalizacao`, `tarifas`, `seguro`, `comissao_permanencia`. Sugerir com base nos alertas do cálculo (ex.: sem taxa anual no contrato sugere capitalização; encargos financiados sugerem tarifas), mas deixar a escolha e o risco com o advogado. Se o duodécuplo for atendido, avisar que a tese de capitalização tende a ser fraca.
3. **Preparar `caso.json`** a partir de `references/exemplo_caso.json`: partes, contrato, teses, tutela pedida, textos de fundamentação específicos do caso (`fundamentos_adicionais_juros`, `tarifas_fundamento`, `seguro_fundamento`, `capitalizacao_fundamento`, `comissao_fundamento`), `fatos_adicionais`, valor da causa e `calculo_arquivo`.
4. **Montar:** `python3 scripts/montar_peca.py caso.json peca.md`. O script junta os módulos de `assets/modulos/` conforme as teses, numera as seções, preenche os números com formatação em reais e percentuais, valida as citações contra a legal-kb e gera `peca.relatorio.json`.
5. **Tratar o relatório.** Resolver cada `campos_a_preencher` (perguntando ao advogado o que só ele sabe), cada `citacoes_fora_da_base` (remover ou levar à conferência) e repassar os `avisos_de_status_e_conferencia`. O Tema 1.378 aparece sempre como pendente na seção de juros: manter o alerta ao advogado.
6. **Entregar** o rascunho em Word (skill `docx`) ou em documento editável, com as notas ao advogado visíveis. Só gerar a versão limpa (`--sem-notas`) quando o advogado confirmar que as notas foram resolvidas.

## Regras de redação

- **Números só do cálculo.** Se o advogado pedir para ajustar um valor, ajustar o cálculo e regenerar, nunca editar o texto.
- **Fundamentos do caso concreto.** O módulo de juros exige fundamentos além da comparação com a taxa média, porque a média sozinha não basta (REsp 2.200.194/RS) e o Tema 1.378 está pendente. Não preencher esses campos com generalidades; pedir ao advogado os elementos (captação, spread, risco, garantia, idade do veículo).
- **Tutela com cautela.** O módulo de tutela traz nota sobre as Súmulas 380 e Tema 972 (a propositura da revisional e a abusividade de encargos acessórios não afastam a mora por si). Não prometer ao cliente nem escrever na peça que a mora está descaracterizada.
- **Dobro com modulação.** O texto do indébito separa pagamentos antes e depois de 30/3/2021. Não pedir dobro para o período anterior sem prova de má-fé.
- **Não inventar fatos.** Se o fato não estiver no contrato, nos documentos ou na fala do advogado, deixar `[[PREENCHER]]`.
- **Citações:** só as da legal-kb. Para acrescentar um precedente, seguir o fluxo de inclusão daquela skill (conferência humana primeiro).

## Estrutura gerada

I. Gratuidade · II. Conciliação · III. Fatos · IV. Direito (um subtítulo por tese) · V. Obrigações controvertidas e valor incontroverso · VI. Repetição do indébito · VII. Tutela de urgência (se pedida) · VIII. Pedidos (inclui inversão do ônus, perícia contábil e valor da causa).

Os módulos ficam em `assets/modulos/`. Para ajustar o estilo do escritório, editar os módulos (mantendo os `{{campos}}`); para uma tese nova, criar o módulo e registrá-lo em `MODULO_POR_TESE` no script.

## Limites

Cobre financiamento de veículo com alienação fiduciária e as teses acima. Não cobre ação de busca e apreensão em defesa (contestação), embargos, nem peças tributárias. A calibragem de risco processual, o valor da causa e a estratégia (pedir ou não tutela, depositar ou não) são do advogado. Dados reais de clientes: usar a skill `compliance-oab-lgpd` antes de enviar texto a serviços externos.
