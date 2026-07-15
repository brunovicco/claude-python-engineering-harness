# Validation report

Validated on 2026-07-15 with Claude Code 2.1.208, Python 3.13.2, and uv 0.11.x.

## Harness

- 22 repository regression tests passed.
- Python compilation, Ruff, workflow syntax, and whitespace checks passed.
- Plugin and marketplace validation passed with the Claude Code CLI.
- Tests cover rendering, merge conflicts, symlink confinement, validator regressions, hook failure
  behavior, MCP classification, changed-file secret scanning, and template/plugin parity.

## Rendered project

A fresh Python 3.13 project named `release-candidate` was rendered and validated:

| Check | Result |
|---|---|
| Lock and frozen dependency sync | Passed |
| Ruff lint and format | Passed |
| Architecture and MCP validators | Passed |
| Strict Mypy | Passed |
| Pytest | 12 passed |
| Coverage | 96.67% |
| Bandit | No findings |
| pip-audit | No known dependency vulnerabilities |

The generated wheel, source package, and container were validated in the preceding 0.3.0 release;
they were not rebuilt in this pass.
