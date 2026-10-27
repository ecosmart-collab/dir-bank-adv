# Revisional — calculadora de revisão de contratos bancários

Ferramenta interna para escritório de advocacia bancária (atuação contra bancos). Faz o recálculo de financiamentos pela Tabela Price, apura o indébito e gera demonstrativo para impressão/PDF.

## O que faz

- **Taxa efetiva real**: deduz a taxa mensal implícita na parcela cobrada e compara com a taxa contratada.
- **Comparação com taxa de referência** (ex.: média BACEN na data da contratação), com alerta quando a taxa efetiva é ≥ 1,5x a referência.
- **Exclusão de encargos financiados** (TAC, tarifas, seguro prestamista) no recálculo.
- **Indébito parcela a parcela**, com correção monetária, juros de mora simples e opção de repetição em dobro.
- **Saldo devedor** contratual × revisado.
- **Casos salvos** com busca, **exportar CSV** e **laudo para impressão**.

## Arquivos

| Arquivo | Função |
|---|---|
| `index.html` | Interface (app de página única) |
| `calc.js` | Motor de cálculo (funciona no navegador e no Node) |
| `config.js` | URL e chave pública do Supabase (opcional) |
| `schema.sql` | Tabela `casos` com RLS para o Supabase |
| `test.js` | Testes do motor: `node test.js` |

## Como usar

**Modo local (sem login):** abra `index.html` no navegador. Os casos ficam no próprio navegador.

**Modo escritório (login + banco compartilhado):**
1. Crie um projeto no Supabase e rode `schema.sql` no SQL Editor.
2. Em Authentication > Providers > Email, **desative "Allow new users to sign up"** e crie os usuários do escritório manualmente.
3. Preencha `config.js` com `SUPABASE_URL` e a chave **anon/publishable** (nunca a `service_role`).
4. Publique a pasta em qualquer hospedagem estática (ex.: Nginx na VPS) com HTTPS.

## Modelo de cálculo

- Parcela Price: `PMT = PV · i / (1 − (1+i)^−n)`.
- Taxa efetiva: resolve `PMT(valor, i, n) = parcela cobrada` por bisseção.
- Parcela revisada: `PMT(valor − encargos, taxa de referência, n)`.
- Diferença por parcela = cobrada − revisada. Cada diferença é corrigida pelo índice informado pelos meses até a data-base e acrescida de mora simples.
- Saldo devedor = valor presente das parcelas restantes (contratual à taxa efetiva; revisado à taxa de referência).

## Limitações e cuidados

- Cobre **Tabela Price** de parcelas iguais. SAC, carência, IOF detalhado e contratos com pagamentos irregulares não estão incluídos.
- A **taxa de referência** e o **índice de correção** são digitados pelo usuário. Consulte as séries do BACEN (SGS) e o índice adotado em juízo.
- Os alertas citam parâmetros jurisprudenciais como orientação. Confirme a jurisprudência vigente (inclusive sobre repetição em dobro e tarifas) antes de peticionar.
- Não substitui perícia contábil.

## Próximos passos sugeridos

SAC e outros sistemas, busca automática da taxa média no BACEN, geração de petição a partir do caso e agentes para leitura de contratos em PDF.
