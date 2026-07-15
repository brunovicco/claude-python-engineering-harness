# Validation report

Validated on 2026-07-15 with Python 3.13.2 and uv 0.11.28.

## Harness

- 38 repository regression tests passed.
- Python compilation, Ruff, workflow syntax, and whitespace checks passed.
- Tests cover rendering, merge conflicts, symlink confinement, validator regressions, hook failure
  behavior, MCP classification, changed-file secret scanning, all three profiles, manifest upgrades,
  dry-run/check behavior, branch alignment, multi-root architecture, and plugin layout independence.
- CI defines a Python 3.12-3.14 × service/library/workspace generated-project matrix, builds the
  service image, and asserts that non-service profiles have no runtime Dockerfile.

## Rendered project

Fresh Python 3.13 `service`, `library`, and `workspace` projects were rendered and validated with
real lock resolution, frozen all-package sync, harness consistency checks, and their complete
project-owned quality gates:

| Check | Result |
|---|---|
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
