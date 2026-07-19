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

## Language policy

English is the canonical language for all documentation. The following documents must also ship a
`.pt-BR.md` sibling, updated in the same change: `docs/LOOPS.md`, `docs/UPGRADING.md`, and
`docs/ENTERPRISE_ROLLOUT.md`. Other documents may be translated opportunistically, but a stale
translation is worse than none: if you cannot update the pair, say so in the pull request. The
sibling `codex-python-engineering-harness` follows the same policy so both harnesses keep the same
language matrix.

## Sibling-harness parity

This harness and `codex-python-engineering-harness` share a parity manifest
(`parity-manifest.json`, byte-identical in both repositories) checked in CI by
`scripts/parity_check.py`. When adding or removing a parity-relevant artifact, update the manifest
in both repositories in the same change, or declare an intentional divergence with a reason in
this repository's `parity-exceptions.json`.

## Release checklist

- Keep changes focused and update tests for behavioral changes.
- Render the template or validate the plugin, as applicable.
- Update `CHANGELOG.md` and `VALIDATION.md` with evidence actually produced.
- Keep plugin and marketplace versions equal.
- Add migration guidance when existing generated repositories require manual action.
- Update a translation when editing a document that still has a translated sibling.
- Do not weaken a quality or security control to make validation pass.
