# Claude Code Python Engineering Harness

Reusable scaffold and Claude Code plugin for consistent Python engineering workflows.

It provides:

- a project template with Python tooling, architecture rules, hooks, agents, skills, and CI;
- an optional plugin for sharing generic agents, skills, and safety hooks;
- opt-in MCP governance and LLM observability;
- deterministic quality gates that complement model-based review.

## Quick start

Create a project:

```bash
python3 bootstrap.py \
  --name payments-api \
  --package payments_api \
  --target ../payments-api \
  --python 3.13 \
  --git-init \
  --lock
```

Apply the harness to an existing repository without replacing existing files:

```bash
python3 bootstrap.py \
  --name existing-service \
  --package existing_service \
  --target ../existing-service \
  --merge
```

Conflicts are written as `.harness-new`, `.harness-new.2`, and so on for manual review.

Then:

```bash
cd ../payments-api
uv sync --frozen
claude
```

Useful skills include `/quality-gate`, `/review-change`, `/security-review`, `/review-mcp`, and
`/prepare-pr`.

## What the project template includes

- `CLAUDE.md` and `AGENTS.md` for persistent project instructions;
- path-scoped rules under `.claude/rules/`;
- focused agents and invocable skills;
- safety, formatting, context, and changed-file scanning hooks;
- Ruff, Mypy, Pytest, Bandit, pip-audit, and architecture checks;
- a multi-stage Dockerfile and GitHub Actions workflow;
- optional Langfuse metadata tracing;
- MCP examples, validation, and managed-policy guidance.

The generated service is intentionally framework-neutral. Replace its placeholder container command
and starter modules with the project's actual entrypoint and domain.

## Plugin

Add the repository as a marketplace and install the plugin:

```text
/plugin marketplace add <path-or-repository>
/plugin install python-engineering-harness@python-engineering-standards
```

For personal use across projects:

```bash
claude plugin install \
  python-engineering-harness@python-engineering-standards \
  --scope user
```

Test a local checkout with:

```bash
claude --plugin-dir ./plugin/python-engineering-harness
```

Plugin components are namespaced, for example
`/python-engineering-harness:quality-gate`. The plugin is disabled by default because its hooks can
block actions and modify changed Python files.

## Security model

Instructions shape model behavior; they are not an enforcement boundary. Hooks and permissions add
deterministic guardrails, while managed policy, repository protection, identity controls, network
controls, and OS-level sandboxing provide hard enforcement.

MCP is disabled by default. Treat every server as a new trust and data-egress boundary, use
least-privilege credentials, and keep production mutations outside this harness.

## Customize after rendering

Review these first:

- commands and project identity in `AGENTS.md`;
- layer rules and `scripts/validate_architecture.py`;
- permissions and sensitive paths under `.claude/`;
- `docs/PRIVACY.md`, `docs/MCP.md`, and LLM tracing policy;
- the real package modules, container entrypoint, and deployment-specific checks.

## Requirements and documentation

- Claude Code 2.1.208 or later;
- Python 3.12, 3.13, or 3.14;
- uv and Git;
- macOS, Linux, or WSL for the default hooks.

See [contributing](CONTRIBUTING.md), [validation](VALIDATION.md),
[enterprise rollout](docs/ENTERPRISE_ROLLOUT.md), [upgrading](docs/UPGRADING.md), and
[official sources](SOURCES.md).
