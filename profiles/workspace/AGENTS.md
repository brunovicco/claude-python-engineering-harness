# {{PROJECT_NAME}} engineering contract

## Project

- Runtime: Python {{PYTHON_VERSION}}
- Profile: workspace
- Root: virtual uv project (`package = false`)
- Members: declare real packages explicitly in `[tool.uv.workspace]`

The root is coordination infrastructure, not an artificial Python package. Add no empty package or
service directories and no runtime Dockerfile until a deployable application requires one.

## Quality gate

```bash
uv run python scripts/quality_gate.py
```

The runner discovers configured package source and test roots. Update `pyproject.toml` whenever a
member layout changes. Use `--check NAME` for focused work and run the complete gate before completion.

Keep package ownership and dependency boundaries explicit. Default-deny boundaries belong in
`[tool.engineering-harness.architecture]`; do not embed domain-specific rules in harness scripts.
Never expose secrets or production data, and keep external mutations permission-gated.
