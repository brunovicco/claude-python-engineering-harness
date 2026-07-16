# Evaluation guide

This guide makes the harness claims reproducible. It separates repository checks from checks run in
freshly generated projects and records the commands, expected artifacts, and acceptance criteria.

## Five-minute evaluation

From a clean checkout with Python, Git, and uv installed:

```bash
python3 bootstrap.py --name demo-service --package demo_service \
  --target ../demo-service --profile service --python 3.13 --git-init --lock
cd ../demo-service
uv sync --frozen --all-groups
uv run python scripts/quality_gate.py
```

The generated project should contain:

```text
demo-service/
├── .claude/              # rules, agents, skills, hooks, and settings
├── .github/workflows/    # CI invoking the project-owned quality gate
├── docs/                 # architecture, privacy, MCP, and operations guidance
├── scripts/              # deterministic quality and policy validators
├── src/demo_service/     # Clean Architecture package roots
├── tests/                # starter regression tests
├── .harness.json         # generation metadata and content hashes
├── AGENTS.md
├── CLAUDE.md
├── Dockerfile
└── pyproject.toml
```

## Profile comparison

| Capability | service | library | workspace |
|---|---|---|---|
| Installable root package | Yes | Yes | No |
| Runtime container | Yes | No | No |
| Strict Mypy and tests | Yes | Yes | Per member |
| Clean Architecture boundaries | Yes | Yes | Per configured root |
| Observability starter | Optional | No | Per member |
| Intended use | Deployable backend | Reusable package | Multi-package repository |

## Acceptance criteria

The repository is ready for release when all of the following are true at the release commit:

1. Repository regression tests, compilation, Ruff, workflow syntax, and whitespace checks pass.
2. Fresh `service`, `library`, and `workspace` projects render for every supported Python version.
3. Each generated project passes frozen dependency sync and its own `scripts/quality_gate.py`.
4. The service image builds and runs as a non-root user; non-service profiles emit no Dockerfile.
5. Merge, dry-run, check, conflict numbering, file-mode preservation, and symlink-confinement
   regressions pass.
6. Hook and MCP tests cover malformed input, secret scanning, sensitive paths, trust classification,
   and prohibited literal credentials.
7. `VALIDATION.md` records the date, Python version, release commit, commands, and observed results.

## Recording results

Do not update pass counts by hand without running the corresponding command. For a release, capture:

```bash
git rev-parse HEAD
python3 --version
python3 -m unittest discover -s tests -v
git diff --check
```

Then run the generated-profile matrix in CI or reproduce each supported profile and Python version
locally. Link the successful workflow run from `VALIDATION.md`; do not treat a previous run from a
different commit as evidence for the release.

Pinned Action SHAs and container digests are updated monthly by Dependabot. Review the upstream
release notes and require the complete CI matrix before merging those updates.
