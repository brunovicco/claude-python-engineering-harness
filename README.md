# Claude Code Python Engineering Harness

*[Português](README.pt-BR.md)*

Reusable harness to standardize Python development with Claude Code across engineering teams.

It combines two levels:

1. **Per-project scaffold**: `CLAUDE.md`, `AGENTS.md`, rules, hooks, agents, skills, workflow, Python configuration, and CI versioned in each repository.
2. **Optional plugin**: reusable package with generic agents, skills, and hooks to load into any project.

The design follows the official Claude Code primitives available as of July 2026:

- `CLAUDE.md` for short, persistent instructions;
- `.claude/rules/` for modular, path-conditional rules;
- `.claude/skills/` for repeatable procedures;
- `.claude/agents/` for specialists with their own context and tools;
- deterministic hooks for security, formatting, and session context;
- `.claude/workflows/` for parallel review on larger tasks;
- output style and status line to standardize the interaction;
- plugin for distribution across projects;
- opt-in MCP governance, with validated configuration, protection hooks, and enterprise-policy examples.

## Quick start

Create a new project:

```bash
python3 bootstrap.py \
  --name payments-api \
  --package payments_api \
  --target ../payments-api \
  --python 3.13 \
  --git-init \
  --lock
```

Apply the harness to an existing repository, preserving files that are already present:

```bash
python3 bootstrap.py \
  --name existing-service \
  --package existing_service \
  --target ../existing-service \
  --merge
```

`--merge` mode never overwrites existing files. On conflict, the suggested file is saved with a `.harness-new` suffix for manual review.

## After bootstrapping

```bash
cd ../payments-api
uv sync --frozen
claude
```

In Claude Code:

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

Use `/doctor` to detect configuration problems, `/hooks` to inspect hooks, and `/mcp` to review servers and authentication.

## Reusable plugin

The repository also contains `.claude-plugin/marketplace.json`, enabling distribution through the team's internal marketplace. Example after publishing or cloning the repository:

```text
/plugin marketplace add <path-or-repository-of-the-harness>
/plugin install python-engineering-harness@python-engineering-standards
```

Test the plugin locally in a session:

```bash
claude --plugin-dir ./plugin/python-engineering-harness
```

Components are namespaced, for example:

```text
/python-engineering-harness:quality-gate
/python-engineering-harness:security-review
```

For automatic loading across all projects, copy the plugin directory to `~/.claude/skills/python-engineering-harness/`. In corporate environments, prefer publishing the plugin to an internal marketplace and controlling its installation through managed settings.

The plugin ships disabled by default in the manifest because its hooks alter session behavior. Enable it deliberately after reviewing the scripts.

## MCP: external integration with control

The harness includes an MCP layer but does not connect any server by default. This decision is intentional: every MCP expands the trust boundary, data egress surface, and set of actions available to the agent.

Included components:

- `.mcp.json.example` for project configuration without credentials;
- `docs/MCP.md` covering transports, scopes, authentication, prompt injection, and approval;
- `.claude/rules/mcp.md` with rules loaded when the integration changes;
- `mcp-integrator` for specialized configuration and review;
- `/configure-mcp` and `/review-mcp`;
- `guard_mcp.py` hook, which blocks secret exfiltration and requires confirmation on mutating tools;
- `scripts/validate_mcp_config.py`, run in the quality gate;
- `managed-mcp.json` and managed-settings examples for corporate allowlisting/denylisting.

To start a shared integration:

```bash
cp .mcp.json.example .mcp.json
# Edit endpoints and variable names, never secret values.
uv run python scripts/validate_mcp_config.py
claude
```

Test the server in local scope first. Promote to `.mcp.json` only after a security, data, permissions, and ownership review.

The plugin does not embed a generic MCP server. Hooks, scripts, and native tools already handle local operations with a smaller attack surface; MCP stays reserved for genuine external integrations.

## Design principles

### Instruction is not control

`CLAUDE.md`, rules, and skills guide the model. Policies that must be guaranteed, such as blocking sensitive files or destructive commands, live in hooks and permissions.

### Lean context

The main file is short. Specific rules load only when Claude is working on matching paths. Long procedures are skills and only enter context when used.

### Real gates outside the agent

The harness includes CI, Ruff, Mypy, Pytest, Bandit, and pip-audit. The agent's review complements these tools but does not replace them.

### Fail-closed security on dangerous actions

Hooks block destructive commands and access to sensitive files. Secret detection after a write interrupts the flow and requires a fix.

### Human authorship

Claude does not commit, push, merge, publish, or change infrastructure without an explicit request. Every change must be reviewed, tested, and attributed to a person.

## Structure

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

## Recommended customizations

After creating a project, adjust first:

- run commands in `AGENTS.md`;
- layer boundaries in `.claude/rules/architecture.md`;
- sensitive paths in `.claude/hooks/protect_sensitive_files.py`;
- approved commands in `.claude/settings.json`;
- servers, expected credentials, and ownership in `.mcp.json` and `docs/MCP.md`;
- regulatory requirements in `docs/PRIVACY.md`;
- LLM call tracing (opt-in, off by default) in `docs/LLM_OBSERVABILITY.md` and `.env.example`;
- workflow base branch in `.claude/workflows/review-branch.js`;
- the forbidden-dependency list in `scripts/validate_architecture.py`;
- the real package and modules in `src/`;
- the placeholder `CMD` in `Dockerfile` once the project defines a real entrypoint;
- git worktree isolation (`isolation: worktree` in `python-implementer.md`'s frontmatter) for larger or harder-to-reverse changes - see `docs/DEVELOPMENT.md`.

## Requirements

- Claude Code 2.1.202 or later recommended;
- Python 3.13 by default, configurable in the bootstrap;
- uv;
- Git;
- macOS, Linux, or WSL for the default hook configuration.

Hook scripts use only the Python standard library. The generated project uses uv for quality tooling.

## Official sources consulted

- Claude Code documentation: memory, rules, hooks, settings, subagents, skills, workflows, plugins, MCP, managed MCP, status line, output styles and security.
- Anthropic `claude-code` repository and official plugin examples.
- Astral uv documentation for GitHub Actions and dependency locking.

See `SOURCES.md` for addresses and the review date.
