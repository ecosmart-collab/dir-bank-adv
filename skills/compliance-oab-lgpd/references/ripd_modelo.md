# Relatório de Impacto à Proteção de Dados (RIPD) — Módulo de IA

> Modelo inicial. A LGPD prevê o relatório de impacto (art. 38) e o registro das operações de tratamento (art. 37). Conferir a regulamentação da ANPD vigente. Preencher os campos entre colchetes.

**Controlador:** [escritório, CNPJ] · **Encarregado:** [nome, contato] · **Data/versão:** [__/__/____ — v0.1]

## 1. Descrição do tratamento

- **Finalidade:** prestação de serviços advocatícios em ações revisionais de financiamento de veículos: triagem, leitura de contratos, cálculo e elaboração de minutas.
- **Base legal:** execução de contrato / procedimentos preliminares (art. 7º, V) e exercício regular de direitos em processo judicial (art. 7º, VI). Dados sensíveis (ex.: saúde, em casos de seguro prestamista ou superendividamento) apenas quando indispensáveis, com base no art. 11. [Validar com o responsável]
- **Titulares:** clientes (consumidores) e, eventualmente, terceiros mencionados em documentos.
- **Dados tratados:** identificação (nome, CPF, RG, endereço, contato), dados contratuais e financeiros, dados do veículo, comprovantes de pagamento, comprovantes de renda, documentos processuais.
- **Ciclo de vida:** coleta (canal seguro) → armazenamento (banco com controle de acesso) → uso (pseudonimizado em ferramentas de IA) → retenção ([prazo definido pelo escritório]) → descarte documentado.

## 2. Operadores e transferência internacional

| Operador/ferramenta | Função | Local de processamento | Transferência internacional? | Salvaguardas (DPA, cláusulas, sem treino) |
|---|---|---|---|---|
| [provedor de LLM] | Extração/rascunho | [país] | [sim/não] | [..] |
| [hospedagem/banco] | Armazenamento | [país] | [sim/não] | [..] |
| [mensageria, ex.: WhatsApp] | Atendimento | [..] | [..] | [..] |

Enviar dados a serviços hospedados no exterior pode configurar transferência internacional (art. 33): exige mecanismo legal adequado.

## 3. Necessidade e proporcionalidade

- Minimização: só os dados necessários vão ao modelo; nomes, CPF e endereços são substituídos por tokens (`pseudonimizar.py`).
- O mapa de reversão fica fora do repositório e fora de serviços externos.

## 4. Riscos e medidas

| Risco | Probabilidade | Impacto | Medidas |
|---|---|---|---|
| Vazamento de dados de clientes em ferramenta de terceiros | [M] | [A] | Pseudonimização; ferramentas aprovadas; sem treino; DPA |
| Acesso indevido interno | [M] | [A] | RLS por caso/advogado, MFA, logs de auditoria append-only |
| Dados de cliente no repositório/Git | [M] | [A] | .gitignore, gitleaks com regras de CPF/CNPJ/placa/contrato, dados sintéticos |
| Peça com citação falsa ou desatualizada (alucinação) | [M] | [A] | legal-kb única fonte; validador de citações; revisão humana obrigatória |
| Extração errada de taxa/valor | [M] | [M] | Conferência humana dos campos críticos; trecho e página de cada dado |
| Retenção além do necessário | [B] | [M] | Política de retenção e descarte documentados |
| Incidente de segurança | [B] | [A] | Plano de incidente; comunicação à ANPD e aos titulares quando aplicável (art. 48) |

## 5. Direitos dos titulares

Canal: [e-mail/telefone do encarregado]. Prazo interno de resposta: [__ dias]. Procedimento para acesso, correção, eliminação e informações sobre compartilhamento.

## 6. Aprovação e revisão

Aprovado por: [nome] em [data]. Revisar a cada [6–12] meses, ou quando mudar a ferramenta, o fluxo ou a norma aplicável.
