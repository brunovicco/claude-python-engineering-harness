# {{PROJECT_NAME}}

Python {{PYTHON_VERSION}} project using uv and the team Claude Code engineering harness.

## Development

```bash
uv sync --frozen
uv run pytest
```

## Quality gate

```bash
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
uv run bandit -c pyproject.toml -r src
uv run pip-audit
```

## Container

```bash
docker build -t {{PROJECT_NAME}} .
docker run --rm {{PROJECT_NAME}}
```

`Dockerfile` ships a placeholder `CMD`; replace it with the project's real entrypoint (an ASGI
server, a worker loop, etc.) once one exists.

See `AGENTS.md` for the engineering contract and `docs/ARCHITECTURE.md` for dependency rules.
