---
name: quality-gate
description: Run the complete Python quality gate and summarize failures without changing configuration.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

Choose the gate in this order:

1. If `scripts/quality_gate.py` exists, run `uv run python scripts/quality_gate.py`.
2. Otherwise, run the quality commands declared by the project's `AGENTS.md`, in their order.
3. Only when neither source exists, state that the generic fallback is being used and run Ruff,
   Mypy over existing `src`/`tests`, Pytest, Bandit over existing `src`, and pip-audit.

Do not edit files or weaken settings. Report command, status, key errors, whether each failure is related to the current diff, and the final gate result.
