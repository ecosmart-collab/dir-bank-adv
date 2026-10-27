# Checklist de segurança do ambiente (Supabase, repositório, integrações)

## Banco e armazenamento (Supabase/Postgres)

- [ ] **RLS ativado em todas as tabelas** com políticas por escritório, advogado e caso. Testar políticas com usuários de papéis diferentes.
- [ ] Cadastro aberto desativado; usuários criados por convite. **MFA obrigatório**.
- [ ] Buckets de storage **privados**; acesso por URL assinada de curta duração e políticas por caso.
- [ ] Chave `service_role` apenas no servidor; no front-end, somente a chave pública (anon/publishable).
- [ ] **Tabela de auditoria append-only**: leitura e download de documentos, execução de cálculo, geração de peça, alteração de status.
- [ ] Backups criptografados e teste de restauração periódico.
- [ ] Logs da aplicação sem dados pessoais (mascarar CPF, nome, contrato).

## Repositório (GitHub)

- [ ] Repositório **privado**, em organização, com ruleset na `main`: PR obrigatório, aprovação, CODEOWNERS, checks verdes, sem force push.
- [ ] `gitleaks` no pre-commit e no CI, com as regras de CPF/CNPJ/placa/contrato (`repo_seguranca/gitleaks.toml`).
- [ ] `.gitignore` de dados de clientes (`repo_seguranca/gitignore_clientes.txt`).
- [ ] Fixtures e testes só com **dados sintéticos** (CPF 000.000.000-00 etc.).
- [ ] Segredos em GitHub Secrets/Environments ou cofre; workflows do n8n exportados **sem credenciais**.
- [ ] Dependabot e CodeQL ativos. `SECURITY.md` com canal de reporte e plano de incidente.
- [ ] Atenção: em repositório privado de conta pessoal no plano gratuito, rulesets e branch protection podem não estar disponíveis. Usar organização (plano Team) ou aplicar as proteções por outros meios.

## Ferramentas de IA

- [ ] Somente ferramentas da lista aprovada na política de uso de IA.
- [ ] Provedor sem treino com os dados; retenção mínima; contrato/DPA assinado.
- [ ] Pseudonimização antes do envio de texto; mapa de reversão fora do repositório.
- [ ] Transferência internacional avaliada (LGPD, art. 33).

## Operação

- [ ] Encarregado (DPO) indicado e canal de titulares divulgado.
- [ ] Registro das operações de tratamento (art. 37) e RIPD atualizados.
- [ ] Política de retenção e descarte definida e aplicada ([prazo a definir pelo escritório]).
- [ ] Plano de incidente: contenção, avaliação, comunicação à ANPD e aos titulares quando aplicável (art. 48), registro.
- [ ] Treinamento da equipe e revisão periódica.
