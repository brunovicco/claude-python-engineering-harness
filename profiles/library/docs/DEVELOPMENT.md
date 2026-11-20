# Development guide

```bash
uv sync --frozen
uv run python scripts/quality_gate.py
```

Use `uv run python scripts/quality_gate.py --list` to discover focused checks. Use `claude doctor`
for installation and configuration diagnostics.

Bash commands run in Claude Code's sandbox (`sandbox` in `.claude/settings.json`): writes stay in the
project and tool caches, only PyPI is reachable without asking, and secrets denied to `Read` are
unreadable. Run commands the sandbox cannot host from your own terminal.
