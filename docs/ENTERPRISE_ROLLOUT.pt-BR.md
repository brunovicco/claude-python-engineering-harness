# Rollout corporativo

*[English](ENTERPRISE_ROLLOUT.md)*

Use o scaffold do repositório para política específica de projeto e o marketplace de plugins para capacidades reutilizáveis.

## Ownership recomendado

- Engenharia de plataforma é dona do plugin, do runtime de hooks, das permissões de ferramentas aprovadas e da baseline de CI.
- Segurança é dona dos caminhos bloqueados, padrões de comando perigosos, padrões de segredo e governança de exceções.
- Arquitetura é dona dos contratos de dependência e do template padrão de ADR.
- Cada time de produto é dono do seu `CLAUDE.md`, `AGENTS.md`, regras com escopo de caminho, inventário de dados e critérios de aceite.

## Modelo de distribuição

1. Publique este repositório em um host Git interno controlado.
2. Adicione o `.claude-plugin/marketplace.json` dele como um marketplace interno.
3. Valide e versione o plugin antes da promoção.
4. Fixe ou aprove versões via managed settings onde disponível.
5. Faça o rollout primeiro para um grupo piloto e inspecione negações, falsos positivos, latência e overrides de desenvolvedores.
6. Promova somente depois que o projeto gerado e o plugin passarem no checklist de validação.

## Separação de responsabilidades

- Mantenha fatos e comandos do projeto no repositório.
- Mantenha procedimentos reutilizáveis e especialistas no plugin.
- Mantenha controles obrigatórios em hooks, política de permissões, CI, identidade, rede e proteção do repositório.
- Não coloque credenciais nas configurações do plugin nem na configuração MCP.
- Trate servidores MCP e integrações externas como caminhos de saída de dados que exigem um threat model explícito.

## Modelo de rollout de MCP

Trate o MCP como uma plataforma de integração, não como um toggle de conveniência do desenvolvedor. Progressão recomendada:

1. Inventarie o sistema externo, o dono, as classes de dados, as operações, a autenticação e a retenção.
2. Faça um piloto em escopo `local` com uma identidade somente leitura e dados que não sejam de produção.
3. Revise a implementação do servidor, o processo de release, o pinning de dependências, a exposição a prompt injection e os destinos de rede.
4. Publique servidores de projeto aprovados via `.mcp.json` ou integrações reutilizáveis via um plugin revisado.
5. Aplique um conjunto fixo via `managed-mcp.json` ou um catálogo gerenciado `allowedMcpServers` com `allowManagedMcpServersOnly: true`.
6. Corresponda integrações remotas por URL e integrações locais por comando exato. Não confie em nomes de servidor como controle de segurança.
7. Mantenha credenciais por usuário via OAuth, expansão de variável de ambiente ou um credential helper. Nunca coloque segredos em arquivos gerenciados.
8. Monitore o uso de servidores e ferramentas via OpenTelemetry sem coletar entradas ou saídas completas.
9. Reaprove integrações periodicamente e revogue servidores, escopos e credenciais não utilizados.

Para ambientes estritamente regulados, prefira um conjunto fixo de servidores gerenciados ou desabilite o MCP inteiramente até que cada integração tenha um threat model aprovado.

## Governança de mudanças

Todo release do harness deve incluir:

- versão semântica;
- notas de release e notas de migração;
- evidência de teste para os casos de hook permitidos e negados;
- evidência de validação do plugin;
- declaração de compatibilidade para as versões suportadas de Claude Code e Python;
- instruções de rollback;
- dono nomeado e processo de exceção.

## Métricas

Acompanhe adoção e efetividade dos controles sem coletar código-fonte ou prompts:

- repositórios e desenvolvedores em cada versão do harness;
- negações de hook por categoria, a partir do `.claude/logs/hooks-audit.jsonl` local de cada projeto
  (escrito por `log_event` em `.claude/hooks/_common.py`; uma linha JSON por decisão de
  deny/ask/block com timestamp, nome do hook, categoria, decisão e nome da ferramenta - nunca o
  texto do comando, conteúdo de arquivo ou valores encontrados). Agregue este arquivo centralmente
  através do seu pipeline de log existente; ele não é coletado automaticamente;
- taxas de falso positivo e de override;
- duração do quality gate e categoria de falha;
- tempo para remediar segredos e dependências vulneráveis;
- percentual de projetos com lock files atualizados e tratamento de dados documentado;
- servidores MCP por dono, versão, escopo e prazo de revisão;
- chamadas de ferramenta MCP de leitura versus mutação, negações e taxas de aprovação.
