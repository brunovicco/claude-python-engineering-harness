# Claude Code Python Engineering Harness

*[English](README.md)*

Harness reutilizável para padronizar o desenvolvimento Python com Claude Code em times de engenharia.

Ele combina dois níveis:

1. **Scaffold por projeto**: `CLAUDE.md`, `AGENTS.md`, regras, hooks, agentes, skills, workflow, configuração Python e CI versionados em cada repositório.
2. **Plugin opcional**: pacote reutilizável com agentes, skills e hooks genéricos para carregar em qualquer projeto.

O desenho segue as primitivas oficiais do Claude Code disponíveis em julho de 2026:

- `CLAUDE.md` para instruções curtas e persistentes;
- `.claude/rules/` para regras modulares e condicionais por caminho;
- `.claude/skills/` para procedimentos repetíveis;
- `.claude/agents/` para especialistas com contexto e ferramentas próprias;
- `.claude/workflows/` para revisão paralela em tarefas maiores;
- hooks determinísticos para segurança, formatação e contexto de sessão;
- output style e status line para padronizar a interação;
- plugin para distribuição entre projetos;
- governança MCP opt-in, com configuração validada, hooks de proteção e exemplos de política corporativa.

## Uso rápido

Crie um projeto novo:

```bash
python3 bootstrap.py \
  --name payments-api \
  --package payments_api \
  --target ../payments-api \
  --python 3.13 \
  --git-init \
  --lock
```

Aplicar o harness em um repositório existente, preservando arquivos já presentes:

```bash
python3 bootstrap.py \
  --name existing-service \
  --package existing_service \
  --target ../existing-service \
  --merge
```

O modo `--merge` não sobrescreve arquivos existentes. Quando houver conflito, o arquivo sugerido é salvo com o sufixo `.harness-new` para revisão manual.

## Depois do bootstrap

```bash
cd ../payments-api
uv sync --frozen
claude
```

No Claude Code:

```text
/memory
/agents
/quality-gate
/review-change
/security-review
/review-mcp
/configure-mcp
/prepare-pr
```

Use `/doctor` para detectar problemas de configuração, `/hooks` para inspecionar hooks e `/mcp` para revisar servidores e autenticação.

## Plugin reutilizável

O repositório também contém `.claude-plugin/marketplace.json`, permitindo distribuição pelo marketplace interno do time. Exemplo após publicar ou clonar o repositório:

```text
/plugin marketplace add <caminho-ou-repositório-do-harness>
/plugin install python-engineering-harness@python-engineering-standards
```

Teste o plugin localmente em uma sessão:

```bash
claude --plugin-dir ./plugin/python-engineering-harness
```

Os componentes ficam namespaced, por exemplo:

```text
/python-engineering-harness:quality-gate
/python-engineering-harness:security-review
```

Para carregamento automático em todos os projetos, copie o diretório do plugin para `~/.claude/skills/python-engineering-harness/`. Em ambientes corporativos, prefira publicar o plugin em um marketplace interno e controlar sua instalação por managed settings.

O plugin vem desabilitado por padrão no manifesto porque seus hooks alteram o comportamento da sessão. Habilite-o conscientemente após revisar os scripts.

## MCP: integração externa com controle

O harness inclui uma camada MCP, mas não conecta nenhum servidor por padrão. Essa decisão é intencional: cada MCP amplia a superfície de confiança, saída de dados e ações disponíveis ao agente.

Componentes incluídos:

- `.mcp.json.example` para configuração de projeto sem credenciais;
- `docs/MCP.md` com transportes, escopos, autenticação, prompt injection e aprovação;
- `.claude/rules/mcp.md` com regras carregadas ao alterar a integração;
- `mcp-integrator` para configuração e revisão especializadas;
- `/configure-mcp` e `/review-mcp`;
- `scripts/validate_mcp_config.py`, executado no quality gate;
- hook `guard_mcp.py`, que bloqueia envio de segredos e exige confirmação em ferramentas mutáveis;
- exemplos de `managed-mcp.json` e managed settings para allowlist/denylist corporativa.

Para iniciar uma integração compartilhada:

```bash
cp .mcp.json.example .mcp.json
# Edite endpoints e nomes de variáveis, nunca valores secretos.
uv run python scripts/validate_mcp_config.py
claude
```

Primeiro teste o servidor em escopo local. Promova para `.mcp.json` somente após revisão de segurança, dados, permissões e ownership.

O plugin não embute um servidor MCP genérico. Hooks, scripts e ferramentas nativas já resolvem operações locais com menor superfície de ataque; MCP fica reservado a integrações externas reais.

## Princípios de desenho

### Instrução não é controle

`CLAUDE.md`, regras e skills orientam o modelo. Políticas que precisam ser garantidas, como bloqueio de arquivos sensíveis ou comandos destrutivos, ficam em hooks e permissões.

### Contexto enxuto

O arquivo principal é curto. Regras específicas são carregadas apenas quando Claude trabalha em caminhos correspondentes. Procedimentos extensos são skills e só entram no contexto quando usados.

### Gates reais fora do agente

O harness inclui CI, Ruff, Mypy, Pytest, Bandit e pip-audit. A revisão do agente complementa essas ferramentas, mas não as substitui.

### Segurança fail-closed nas ações perigosas

Os hooks bloqueiam comandos destrutivos e acesso a arquivos sensíveis. A detecção de segredos após escrita interrompe o fluxo e exige correção.

### Autoria humana

Claude não faz commit, push, merge, publicação ou alteração de infraestrutura sem solicitação explícita. Toda mudança deve ser revisada, testada e atribuída a uma pessoa.

## Estrutura

```text
.
├── bootstrap.py
├── .claude-plugin/marketplace.json
├── docs/ENTERPRISE_ROLLOUT.md
├── template/
│   ├── CLAUDE.md
│   ├── AGENTS.md
│   ├── .mcp.json.example
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── src/
│   ├── tests/
│   ├── docs/
│   ├── .claude/
│   │   ├── settings.json
│   │   ├── rules/
│   │   ├── agents/
│   │   ├── skills/
│   │   ├── hooks/
│   │   ├── workflows/
│   │   └── output-styles/
│   └── .github/workflows/quality.yml
└── plugin/python-engineering-harness/
    ├── .claude-plugin/plugin.json
    ├── agents/
    ├── skills/
    ├── hooks/hooks.json
    ├── scripts/
    └── output-styles/
```

## Customizações recomendadas

Após criar um projeto, ajuste primeiro:

- comandos de execução em `AGENTS.md`;
- limites entre camadas em `.claude/rules/architecture.md`;
- caminhos sensíveis em `.claude/hooks/protect_sensitive_files.py`;
- comandos aprovados em `.claude/settings.json`;
- servidores, credenciais esperadas e ownership em `.mcp.json` e `docs/MCP.md`;
- requisitos regulatórios em `docs/PRIVACY.md`;
- tracing de chamadas LLM (opt-in, desligado por padrão) em `docs/LLM_OBSERVABILITY.md` e `.env.example`;
- branch-base do workflow `.claude/workflows/review-branch.js`;
- lista de dependências proibidas em `scripts/validate_architecture.py`;
- pacote e módulos reais em `src/`;
- o `CMD` placeholder em `Dockerfile` assim que o projeto definir um entrypoint real;
- isolamento em git worktree (`isolation: worktree` no frontmatter de `python-implementer.md`) para mudanças maiores ou difíceis de reverter - ver `docs/DEVELOPMENT.md`.

## Requisitos

- Claude Code 2.1.202 ou superior recomendado;
- Python 3.13 por padrão, configurável no bootstrap;
- uv;
- Git;
- macOS, Linux ou WSL para a configuração padrão de hooks.

Os scripts dos hooks usam apenas a standard library do Python. O projeto gerado usa uv para as ferramentas de qualidade.

## Fontes oficiais consultadas

- Claude Code documentation: memory, rules, hooks, settings, subagents, skills, workflows, plugins, MCP, managed MCP, status line, output styles and security.
- Anthropic `claude-code` repository and official plugin examples.
- Astral uv documentation for GitHub Actions and dependency locking.

Consulte `SOURCES.md` para os endereços e a data da revisão.
