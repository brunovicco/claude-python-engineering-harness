# Validation report

*[Português](VALIDATION.pt-BR.md)*

Validated on 2026-07-08 against rendered projects named `mcp-smoke` and `mcp-smoke-312`.

## Passed

- Bootstrap rendering for Python 3.13.
- Alternate rendering for Python 3.12, including Ruff target selection.
- Non-destructive `--merge` behavior and `.harness-new` conflict output.
- No unresolved scaffold tokens in rendered projects.
- JSON parsing for project settings, MCP examples, plugin hooks, plugin manifest, marketplace manifest, and managed-policy examples.
- TOML parsing after scaffold rendering.
- YAML parsing for 48 agent, skill, and path-scoped rule frontmatters.
- Python compilation and Ruff checks for bootstrap, project hooks, MCP validator, and plugin scripts.
- JavaScript syntax validation for the parallel review workflow.
- Architecture validator pass case and deliberate fail-closed behavior.
- MCP configuration validator pass case.
- MCP configuration validator negative cases for:
  - missing timeout;
  - insecure remote HTTP;
  - literal authorization data;
  - deprecated SSE;
  - shell-wrapped stdio process;
  - literal secret environment value.
- MCP hook allow case for a read-only tool.
- MCP hook escalation cases for general and production-targeted mutations.
- MCP hook deny cases for literal sensitive values and secret-access tool names.
- Existing hook deny cases for destructive Git, sensitive-file access, and secret-shaped content.
- `uv lock --check`.
- `ruff check .`.
- `ruff format --check .`.
- Clean Architecture dependency validation.
- MCP configuration validation in the generated quality gate.
- strict Mypy for `src` and `tests`.
- Pytest and the configured coverage threshold.
- Bandit for `src`.
- Source distribution and wheel build.
- Multi-stage `Dockerfile`: rendered project image built successfully with Docker (uv-based
  builder stage, slim non-root runtime stage) and ran its placeholder `CMD` as the non-root
  `app` user.

