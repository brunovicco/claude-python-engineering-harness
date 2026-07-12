# Relatório de validação

*[English](VALIDATION.md)*

Validado em 08/07/2026 contra projetos renderizados chamados `mcp-smoke` e `mcp-smoke-312`.

## Aprovado

- Renderização do bootstrap para Python 3.13.
- Renderização alternativa para Python 3.12, incluindo a seleção do target do Ruff.
- Comportamento não destrutivo do `--merge` e saída de conflito em `.harness-new`.
- Nenhum token de scaffold não resolvido nos projetos renderizados.
- Parsing de JSON para configurações de projeto, exemplos de MCP, hooks de plugin, manifesto de plugin, manifesto de marketplace e exemplos de política gerenciada.
- Parsing de TOML após a renderização do scaffold.
- Parsing de YAML para 48 frontmatters de agentes, skills e regras com escopo de caminho.
- Compilação Python e checagens do Ruff para bootstrap, hooks de projeto, validador de MCP e scripts do plugin.
- Validação de sintaxe JavaScript para o workflow de revisão em paralelo.
- Caso de sucesso do validador de arquitetura e comportamento fail-closed deliberado.
- Caso de sucesso do validador de configuração MCP.
- Casos negativos do validador de configuração MCP para:
  - timeout ausente;
  - HTTP remoto inseguro;
  - dado literal de autorização;
  - SSE descontinuado;
  - processo stdio envolto em shell;
  - valor literal de segredo em variável de ambiente.
- Caso de permissão do hook de MCP para uma ferramenta somente leitura.
- Casos de escalonamento do hook de MCP para mutações gerais e voltadas à produção.
- Casos de negação do hook de MCP para valores sensíveis literais e nomes de ferramentas de acesso a segredo.
- Casos de negação de hooks existentes para Git destrutivo, acesso a arquivo sensível e conteúdo com formato de segredo.
- `uv lock --check`.
- `ruff check .`.
- `ruff format --check .`.
- Validação de dependência da Clean Architecture.
- Validação de configuração MCP no quality gate gerado.
- Mypy estrito para `src` e `tests`.
- Pytest e o limite de cobertura configurado.
- Bandit para `src`.
- Build de source distribution e wheel.
- `Dockerfile` multiestágio: a imagem do projeto renderizado foi construída com sucesso usando
  Docker (estágio de build baseado em uv, estágio de runtime enxuto e não root) e executou seu
  `CMD` de placeholder como o usuário não root `app`.
