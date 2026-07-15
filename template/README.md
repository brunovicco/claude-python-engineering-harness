# {{PROJECT_NAME}}

Python {{PYTHON_VERSION}} project using uv and the team Claude Code engineering harness.

## Development

```bash
uv sync --frozen
uv run pytest
```

## Quality gate

```bash
uv run python scripts/quality_gate.py
```

List or select checks with `--list` and `--check NAME`.

## Container

```bash
docker build -t {{PROJECT_NAME}} .
docker run --rm {{PROJECT_NAME}}
```

`Dockerfile` ships a placeholder `CMD`; replace it with the project's real entrypoint (an ASGI
server, a worker loop, etc.) once one exists.

See `AGENTS.md` for the engineering contract and `docs/ARCHITECTURE.md` for dependency rules.
