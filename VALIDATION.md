# Validation report

Validated on 2026-07-16 with Python 3.13 at source commit
`f54ece8633e30522c8f6295ec3f6cdcb7f3c9410`.

The corresponding [GitHub Actions run](https://github.com/brunovicco/claude-python-engineering-harness/actions/runs/29521026553)
passed. See `docs/EVALUATION.md` for the commands and acceptance criteria required to produce a new
report; results from this commit must not be reused for later releases.

## Harness

- 43 repository regression tests passed.
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
