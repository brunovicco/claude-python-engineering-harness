# Contributing

The repository distributes the project `template/` and the reusable
`plugin/python-engineering-harness/`. Keep shared behavior synchronized across both outputs.

Before contributing, read `SUPPORT.md` and `CODE_OF_CONDUCT.md`. Use the issue forms for bug reports
and feature proposals, and report suspected vulnerabilities privately as described in `SECURITY.md`.

## Local checks

Start with:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q \
  bootstrap.py tests template/.claude/hooks template/scripts \
  plugin/python-engineering-harness/scripts
claude plugin validate ./plugin/python-engineering-harness
claude plugin validate .
```

For template changes, render a project and run its complete quality gate:

```bash
python3 bootstrap.py \
  --name smoke-test \
  --package smoke_test \
  --target /tmp/smoke-test \
  --lock
cd /tmp/smoke-test
uv sync --frozen --all-groups
uv run python scripts/quality_gate.py
```

Do not use `from __future__ import annotations` in harness or generated Python. Supported Python
versions already provide the required annotation syntax; quote an individual forward reference
only when evaluation order requires it.

## Source ownership

- `template/CLAUDE.md` and `template/AGENTS.md`: persistent project contract.
- `template/.claude/rules/`: detailed path-scoped standards.
- `template/.claude/hooks/` and plugin `scripts/`: synchronized safety behavior.
- `template/.claude/agents/` and `skills/`: project copies; plugin equivalents use namespaced agents.
- `template/scripts/`: deterministic project validators.

Prefer changing the canonical template first, then port the equivalent plugin change. The regression
suite verifies that duplicated Python scripts remain identical.

## Release checklist

- Keep changes focused and update tests for behavioral changes.
- Render the template or validate the plugin, as applicable.
- Update `CHANGELOG.md` and `VALIDATION.md` with evidence actually produced.
- Keep plugin and marketplace versions equal.
- Add migration guidance when existing generated repositories require manual action.
- Update a translation when editing a document that still has a translated sibling.
- Do not weaken a quality or security control to make validation pass.
