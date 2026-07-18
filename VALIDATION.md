# Validation report

## Current validation — Phase 0-1

Validated on 2026-07-18 for the report-only Evidence-Gated Engineering Loop foundation.

### Identity and provenance

- Published repository commit:
  `388cd8bd8e96c3ffe0b6e464a86ee6e0c6f54f2f`.
- Harness, plugin, and marketplace version: `0.6.0`.
- Shared schemas: `v0.1.2` at
  `0459d61b7b1d4e7b46709e6d3895770553e6fab0`.
- Final integration: pull request
  [#4](https://github.com/brunovicco/claude-python-engineering-harness/pull/4).
- The pull-request quality run validated source head
  `b5c79dd0ab4d12a9072c0c0019ff3750b3d74777` before GitHub recreated the commit through squash
  merge:
  <https://github.com/brunovicco/claude-python-engineering-harness/actions/runs/29660572516>.

### Results

- Regression tests: 56 passed.
- Python compilation: passed.
- Ruff lint: passed.
- JavaScript workflow syntax: passed.
- Whitespace validation with `git diff --check`: passed.
- `loop-schema-vendor`: passed for `v0.1.2`.
- Positive bundle-integrity test: passed.
- Manual-tampering detection test: passed.
- Harness self-evaluation: `Overall: PASS`.
- Complete quality gates passed for all six profile/governance combinations:
  - `service-none`;
  - `service-agentic`;
  - `library-none`;
  - `library-agentic`;
  - `workspace-none`;
  - `workspace-agentic`.

### Scope and limitations

This validation covers Phase 0-1 only. The repository can validate contracts, execute existing
quality gates, verify vendored-schema integrity, render temporary profiles, and produce reports.
It does not provide a loop runner, state machine, evaluator runtime, autonomous candidate creation,
candidate promotion, merge, or deployment.

The builder's report remains non-authoritative. A quality gate is the technical authority, and
human review remains required before any promotion decision.

The self-evaluation workflow still uses the previously pinned `setup-uv` action while the main
quality workflow uses the newer approved pin. Aligning those pins is CI maintenance and should be
performed in a separate change from this documentation record.

### Reproduce the Phase 0-1 validation

```bash
python -m unittest discover -s tests -v
python -m compileall -q bootstrap.py template/.claude/hooks template/scripts \
  plugin/python-engineering-harness/scripts scripts
uvx --from ruff==0.15.20 ruff check --isolated bootstrap.py tests \
  template/.claude/hooks template/scripts plugin/python-engineering-harness/scripts scripts
node --check template/.claude/workflows/review-branch.js
python scripts/loop_self_evaluation.py --output-dir build/loop-self-evaluation
git diff --check
```

## Previous validation — 2026-07-16

Validated on 2026-07-16 with Python 3.13 at source commit
`97cbabcf4d0cf86ad0a7dcf8c8d1fd28dc5a58fe`.

The corresponding [GitHub Actions run](https://github.com/brunovicco/claude-python-engineering-harness/actions/runs/29539700291)
passed. See `docs/EVALUATION.md` for the commands and acceptance criteria required to produce a new
report; results from this commit must not be reused for later releases.

## Harness

- 44 repository regression tests passed.
- Python compilation, Ruff, workflow syntax, and whitespace checks passed.
- Tests cover rendering, merge conflicts, symlink confinement, validator regressions, hook failure
  behavior, MCP classification, changed-file secret scanning, all three profiles, manifest upgrades,
  dry-run/check behavior, branch alignment, multi-root architecture, and plugin layout independence.
- Governance source-catalog validation passed for 11 controls, four capability profiles, and three
  overlays. Regression tests cover profile composition, duplicate-overlay rejection, untreated
  high risks, expired exceptions, and Claude-specific evidence paths.
- CI defines a Python 3.12-3.14 × service/library/workspace generated-project matrix, builds the
  service image, and asserts that non-service profiles have no runtime Dockerfile.

## Rendered project

Fresh Python 3.13 `service`, `library`, and `workspace` projects were rendered and validated with
real lock resolution, frozen all-package sync, harness consistency checks, and their complete
project-owned quality gates:

| Check | service | library | workspace |
|---|---|---|---|
| Git branch and CI alignment | Passed | Passed | Passed |
| Lock and frozen all-package sync | Passed | Passed | Passed |
| Ruff lint and format | Passed | Passed | Passed |
| Architecture and MCP validators | Passed | Passed | Passed |
| Strict Mypy | Passed | Passed | Skipped: no members |
| Pytest | 12 passed | 1 passed | Skipped: no members |
| Coverage | 96.67% | 100% | Not applicable |
| Bandit | No findings | No findings | Skipped: no members |
| pip-audit | No known vulnerabilities | No known vulnerabilities | No known vulnerabilities |

The service and library projects built during `uv sync`; the workspace remained a virtual root and
did not create an artificial package or runtime container.
