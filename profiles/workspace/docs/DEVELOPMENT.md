# Workspace development

```bash
uv sync --frozen --all-packages
uv run python scripts/quality_gate.py
```

Add real workspace members to `pyproject.toml`, along with their source and test root patterns. Use
`claude doctor` for installation and configuration diagnostics.

Bash commands run in Claude Code's sandbox (`sandbox` in `.claude/settings.json`): writes stay in the
project and tool caches, only PyPI is reachable without asking, and secrets denied to `Read` are
unreadable. Run commands the sandbox cannot host from your own terminal.
