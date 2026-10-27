# Política interna de uso de inteligência artificial — [NOME DO ESCRITÓRIO]

> Modelo para adaptação e aprovação pelos sócios. Versão: 0.1 · Data: [__/__/____] · Responsável: [nome, OAB].
> Baseada na Recomendação CFOAB 001/2024 (conferir o texto oficial e atos posteriores da OAB) e na LGPD.

## 1. Princípios

1. **Supervisão humana.** Nenhuma decisão jurídica é tomada por IA. A IA apoia; o advogado decide, revisa e assina. A dependência excessiva de ferramentas de IA é incompatível com a prática da advocacia.
2. **Sigilo e proteção de dados.** Dados de clientes só entram em ferramentas aprovadas e, sempre que possível, pseudonimizados.
3. **Veracidade.** Nenhuma citação de lei, súmula ou precedente entra em peça sem constar da base curada do escritório (legal-kb) e sem conferência no portal oficial.
4. **Transparência com o cliente.** O uso de IA é informado ao cliente antes de começar (cláusula no contrato de honorários) e o cliente pode falar com uma pessoa a qualquer momento.
5. **Rastreabilidade.** Fica registrado o que foi gerado por IA, quem revisou e quando.

## 2. Usos permitidos

- Triagem e organização de informações do cliente (com identificação do atendimento automatizado).
- Leitura e extração de dados de contratos, com conferência humana dos campos críticos.
- Cálculos por motor determinístico versionado, conferidos pelo advogado.
- Rascunho de peças e notificações, sempre revisados integralmente pelo advogado.
- Pesquisa e resumo de jurisprudência, sempre conferidos na fonte oficial.

## 3. Usos proibidos

- Protocolar peça ou enviar comunicação ao cliente, ao banco ou ao tribunal sem aprovação humana.
- Citar jurisprudência ou doutrina não conferida.
- Inserir dados pessoais identificáveis de clientes em ferramentas não aprovadas ou em contas pessoais.
- Usar IA para decidir tese, estratégia, acordo ou valores sem análise do advogado.
- Treinar modelos com dados de clientes sem base legal e autorização.

## 4. Ferramentas aprovadas

| Ferramenta | Finalidade | Dados permitidos | Retenção/treino | Contrato/DPA | Aprovada por |
|---|---|---|---|---|---|
| [ex.: provedor de LLM] | Rascunho e extração | Pseudonimizados | [sem treino / retenção mínima] | [sim/não] | [nome] |

Qualquer ferramenta nova precisa de aprovação do responsável antes do uso. Preferir provedores que não usem os dados para treinar modelos e ofereçam retenção mínima.

## 5. Procedimentos

- **Pseudonimização** antes de enviar texto a serviços externos (skill `compliance-oab-lgpd`, `scripts/pseudonimizar.py`).
- **Registro de uso:** peça ou análise com apoio de IA registra: data, ferramenta, finalidade, revisor.
- **Revisão de peça:** checklist em `checklist_revisao_peca.md`.
- **Incidentes** (vazamento, envio indevido, citação falsa detectada): comunicar ao responsável no mesmo dia, conforme o plano de incidente.

## 6. Treinamento e revisão

Treinar a equipe ao entrar e a cada alteração relevante. Revisar esta política a cada [6] meses ou quando a OAB ou a ANPD publicarem normas novas.

Aprovação: [sócio responsável] — [data]
