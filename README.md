# Claude Code Python Engineering Harness

Reusable scaffold and Claude Code plugin for consistent Python engineering workflows.

It provides:

- explicit `service`, `library`, and `workspace` profiles without making the default a monorepo;
- a project-owned quality runner shared by CI, documentation, skills, and agents;
- an optional plugin for sharing generic agents, skills, and safety hooks;
- opt-in MCP governance and LLM observability;
- opt-in, machine-readable governance profiles and regulatory overlays;
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

`service` is the compatibility-preserving default. Select `--profile library` for a framework-
neutral package or `--profile workspace` for a virtual uv root with no artificial package or
runtime container.

Governance is an independent generator dimension and remains disabled by default. Enable a
capability profile and any additive regulatory overlays when the project needs them:

```bash
python3 bootstrap.py \
  --name payments-api \
  --package payments_api \
  --target ../payments-api \
  --governance-profile agentic \
  --governance-overlay dora \
  --governance-overlay iso-iec-42001
```

Governance profiles are `none`, `baseline`, `ai-assisted`, and `agentic`. Available overlays are
`dora`, `iso-iec-42001`, and `nist-sp-800-53`. They select versioned controls and evidence
requirements; they do not claim that a repository or organization is compliant or certified.

Apply the harness to an existing repository without replacing existing files:

```bash
python3 bootstrap.py \
  --name existing-service \
  --package existing_service \
  --target ../existing-service \
  --merge
```

Conflicts are written as `.harness-new`, `.harness-new.2`, and so on for manual review.
Previously generated, unmodified files are updated automatically using hashes from `.harness.json`;
customized files are never silently replaced.

Preview or audit a project:

```bash
python3 bootstrap.py --name payments-api --package payments_api \
  --target ../payments-api --profile service --dry-run
python3 bootstrap.py --target ../payments-api --check
```

Then:

```bash
cd ../payments-api
uv sync --frozen --all-groups
uv run python scripts/quality_gate.py
claude
```

Useful skills include `/quality-gate`, `/review-change`, `/security-review`, `/review-mcp`, and
`/prepare-pr`.

For a short hands-on walkthrough, generated tree, profile comparison, and explicit acceptance
criteria, see the [evaluation guide](docs/EVALUATION.md).

## Profiles

- `service` keeps Pydantic, structlog, Clean Architecture, Docker, and optional Langfuse tracing.
- `library` emits a buildable `src` package without framework, Docker, or mandatory observability.
- `workspace` emits a virtual uv root (`package = false`) with configurable multi-root discovery,
  no artificial root package, and no runtime Dockerfile.

All profiles share security hooks, MCP policy, CI, `.harness.json`, and
`scripts/quality_gate.py`. Architecture roots and default-deny package boundaries live under
`[tool.engineering-harness.architecture]` in `pyproject.toml`.

## What generated projects include

- `CLAUDE.md` and `AGENTS.md` for persistent project instructions;
- path-scoped rules under `.claude/rules/`;
- focused agents and invocable skills;
- safety, formatting, context, and changed-file scanning hooks;
- Ruff, Mypy, Pytest, Bandit, pip-audit, and configurable architecture checks;
- a GitHub Actions workflow that invokes the same project quality runner;
- service-only Docker and optional Langfuse metadata tracing;
- MCP examples, validation, and managed-policy guidance.
- when enabled, a control catalog snapshot, inventories, assessments, schemas, risk records, and a
  governance gate that writes metadata-only evidence under `build/governance-evidence/`.

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
- source roots and boundaries under `[tool.engineering-harness.architecture]`;
- permissions and sensitive paths under `.claude/`;
- `docs/PRIVACY.md`, `docs/MCP.md`, and LLM tracing policy;
- the selected `governance/` profile, ownership, risks, inventories, assessments, and exceptions;
- the real package modules, container entrypoint, and deployment-specific checks.

## Requirements and documentation

- Claude Code 2.1.208 or later;
- Python 3.12, 3.13, or 3.14;
- uv and Git;
- macOS, Linux, or WSL for the default hooks.

See [contributing](CONTRIBUTING.md), [validation](VALIDATION.md),
[enterprise rollout](docs/ENTERPRISE_ROLLOUT.md), [upgrading](docs/UPGRADING.md), and
[evaluation](docs/EVALUATION.md), and [official sources](SOURCES.md).
