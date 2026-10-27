---
name: leitor-contrato-financiamento
description: Lê contratos de financiamento de veículo (CCB/CDC, PDF ou imagem) e extrai taxas, CET, valor financiado e liberado, parcelas, datas, encargos financiados (TAC, tarifas, registro, avaliação, seguro), cláusulas de mora e comissão de permanência, em JSON com página, trecho literal e nível de confiança, apontando os campos que exigem conferência humana. Use sempre que o usuário enviar ou mencionar contrato, CCB, cédula, proposta de financiamento, extrato do contrato ou pedir para "ler o contrato do cliente", "extrair as taxas", "montar os dados para o cálculo", mesmo sem citar a skill.
---

# Leitor de contrato de financiamento

## Princípio: a IA extrai, o código valida, o humano confere

Uma taxa lida errada contamina o cálculo, a petição e a estratégia. Por isso cada dado extraído vem com **página, trecho literal e confiança**, e nada segue adiante sem conferência humana dos campos críticos. O leitor nunca completa um dado ausente por dedução: se o contrato não diz, o campo fica nulo com `nao_encontrado: true`. Isso é, por si só, uma informação útil (por exemplo, contrato sem taxa anual).

## Fluxo

1. **Abrir o documento.** PDF com texto: skills `pdf-reading` ou `pdf`. PDF escaneado ou foto: usar OCR e registrar `qualidade_leitura` (boa/regular/ruim). Em qualidade ruim, avisar o usuário logo e baixar a confiança dos campos afetados.
2. **Minimizar dados pessoais.** Antes de enviar trechos a qualquer serviço externo, aplicar a skill `compliance-oab-lgpd` (pseudonimização). O leitor não precisa de nome, CPF nem endereço do cliente para extrair taxas e valores; esses dados ficam fora do JSON, e o nome do arquivo não deve conter dados pessoais.
3. **Extrair** no formato de `references/schema_contrato.json`. Para cada dado: `valor`, `pagina`, `confianca`, `trecho`.
   - `alta`: texto claro e inequívoco. `media`: alguma dúvida (OCR ruim, ambiguidade entre campos). `baixa`: ilegível ou suposição, preferir deixar nulo.
   - Taxas como **fração** (1,99% = 0.0199). Datas `AAAA-MM-DD`. Valores como número.
   - Onde olhar: quadro-resumo das primeiras páginas (CCB), cláusulas de encargos e "demonstrativo de crédito", cláusulas de inadimplência, anexo de seguro, termos de garantia.
4. **Encargos financiados:** listar um por um (tipo, valor, se foi financiado, página). Conferir com a diferença entre valor total financiado e valor liberado: se não fechar, procurar o encargo que falta (IOF, seguro, gravame).
5. **Validar:** `python3 scripts/validar_extracao.py extracao.json --calc-out entrada_calculo.json`. O script confere estrutura, lista os campos a conferir e roda consistências (parcela × taxa, duodécuplo, CET, datas, encargos × valor liberado).
6. **Conferência humana.** Apresentar ao advogado a lista de `campos_a_conferir` e os `alertas`, com página e trecho de cada campo crítico para ele abrir o contrato e confirmar. Só depois de preencher `conferencia_humana.conferido_por` e `conferido_em` o status passa a `CONFERIDO`. Peça e cálculo definitivos usam apenas extração conferida.
7. **Encadear:** o esqueleto `entrada_calculo.json` segue para a skill `calculo-revisional-veiculos`, que ainda precisa da taxa de referência BACEN, da data-base, dos pagamentos e dos regimes de correção.

## Como tratar os alertas

- **Parcela lida diferente da calculada pela taxa informada:** pode ser erro de leitura ou a própria evidência de que a taxa efetiva é maior que a declarada. Reabrir a página, conferir valor, prazo e taxa; se tudo estiver certo, destacar ao advogado como achado.
- **Taxa anual ausente ou menor que o duodécuplo:** apontar para a análise de capitalização (Súmulas 539 e 541/STJ). Registrar o trecho da cláusula, se houver.
- **TAC/TEC em contrato posterior a 30/4/2008:** ponto forte potencial (Temas 618 e 619; Súmula 565). Conferir a data com cuidado.
- **Seguro sem documento apartado ou sem opção de escolha:** relevante para o Tema 972. Se o contrato mostra que havia opção, registrar também (isso enfraquece a tese).
- **Valor financiado − liberado ≠ soma dos encargos financiados:** procurar encargo não extraído.

## O que fazer quando o documento é ruim

Contrato cortado, páginas faltando ou ilegível: registrar `observacoes`, marcar os campos como `nao_encontrado`, e pedir ao cliente (via equipe) a via completa. Nunca "reconstruir" cláusulas ausentes.

## Limites

O leitor não interpreta teses nem calcula abusividade. Não substitui a leitura do contrato pelo advogado nos pontos que sustentam a ação. Contratos de leasing, consórcio e empréstimo pessoal têm estrutura diferente: o esquema serve de base, mas os campos podem precisar de adaptação.
