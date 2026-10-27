---
name: prazos-processuais
description: Calcula e organiza prazos processuais cíveis (CPC) do escritório de advocacia bancária — contestação, réplica, apelação, agravo, embargos, cumprimento de decisão — contando dias úteis, publicação no DJe, feriados informados, suspensão de 20/12 a 20/01 e prazo em dobro, e gera data fatal mais data-alvo interna. Use sempre que o usuário perguntar "qual o prazo", "quando vence", "contar prazo", "intimação", "publicação no DJe", "prazo para contestar/recorrer/emendar", ou pedir agenda/alerta de prazos do escritório. Resultado é auxiliar, nunca substitui a conferência do advogado no calendário do tribunal.
---

# Prazos processuais (apoio, não decisão)

Perder prazo é o erro mais caro da advocacia. Por isso esta skill é **conservadora**: calcula com regras explícitas, mostra o raciocínio, avisa quando faltam dados e **sempre exige conferência humana**. O cálculo é feito por código (`scripts/contar_prazo.py`), nunca "de cabeça" pelo modelo.

## Fluxo

1. **Coletar** (perguntar o que faltar): data do evento (disponibilização no DJe ou ciência da intimação/citação), tribunal e comarca, rito (Juizado ou vara cível), prazo em dias e o fundamento (ver `references/prazos_comuns.md`), se há prazo em dobro ou litisconsortes.
2. **Feriados:** pedir a lista de feriados e dias sem expediente **do tribunal e da comarca** para o período. Sem ela o script avisa `SEM_FERIADOS` e o resultado não é confiável. Não inventar feriados locais.
3. **Montar o JSON** (modelo em `scripts/exemplo_entrada.json`) e rodar `python3 scripts/contar_prazo.py entrada.json`.
4. **Entregar** ao advogado: vencimento fatal, data-alvo interna (2 dias úteis antes), todos os avisos e o passo a passo da contagem. Pedir conferência no calendário do tribunal.
5. **Registrar** no sistema do escritório (tabela de prazos do app) com responsável e alertas.

## Regras implementadas (conferir sempre o texto vigente)

- Dias úteis, não corridos (CPC art. 219); nos Juizados Especiais também úteis (Lei 9.099/95, art. 12-A).
- Exclui o dia do começo e inclui o do vencimento; começa no primeiro dia útil seguinte (art. 224 e §3º).
- DJe: disponibilização num dia, publicação no primeiro dia útil seguinte, contagem a partir do dia útil após a publicação (art. 224 §§2º–3º).
- Suspensão de 20/12 a 20/01, inclusive (art. 220): os dias não contam.
- Multiplicador para prazo em dobro (ex.: Defensoria Pública, Fazenda, MP, litisconsortes com procuradores de escritórios distintos em autos físicos — art. 229): o script aplica o multiplicador informado; confirmar o fundamento.
- Data-alvo interna: 2 dias úteis antes do fatal, para revisão e protocolo com folga.

## O que o script NÃO resolve (avisar o advogado)

- **Termo inicial da intimação eletrônica**: ciência por consulta ou decurso do prazo tácito de 10 dias (Lei 11.419/2006, art. 5º). Informar a data efetiva extraída dos autos.
- Feriado local, suspensão do expediente, indisponibilidade do sistema e prazos específicos do tribunal.
- Prazos materiais, prescrição e decadência (CC) — outro cálculo.
- Prazos em processos de outros ramos (trabalhista, penal) ou com regra própria.
- Recursos: tempestividade depende do protocolo, preparo e da comprovação de feriado local no ato (art. 1.003 §6º).

## Frase de segurança no output

Sempre encerrar com: "Prazo calculado de forma auxiliar. Confira no calendário do tribunal e nos autos antes de depender desta data."

## Testes

`python3 scripts/test_contar_prazo.py` (deve imprimir OK).
