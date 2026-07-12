# Contributing

*[Português](CONTRIBUTING.pt-BR.md)*

This repository has no application code of its own to build or test. What you are contributing to
is `template/` (rendered into other repositories by `bootstrap.py`) and
`plugin/python-engineering-harness/` (loaded directly as a Claude Code plugin). Validate changes by
exercising those outputs, not by running a test suite at the repo root - there isn't one.

## Before you start

Read `CLAUDE.md` first. It explains why the two distribution mechanisms exist, that they must be
kept in sync deliberately, and which files are the source of truth for engineering standards
(`template/CLAUDE.md`) versus Claude-Code-specific behavior (`template/AGENTS.md`).

## Changing `template/`

1. Edit the files under `template/`. Remember that `{{PROJECT_NAME}}`, `{{PACKAGE_NAME}}`,
   `{{PYTHON_VERSION}}`, and `{{RUFF_TARGET_VERSION}}` are replaced in both file contents and paths;
   any new file must stay token-clean outside `src/{{PACKAGE_NAME}}/`.
2. Render the template and run its own quality gate:

   ```bash
   python3 bootstrap.py --name smoke-test --package smoke_test --target /tmp/smoke-test \
     --git-init --lock
   cd /tmp/smoke-test
   uv run ruff check .
   uv run ruff format --check .
   uv run python scripts/validate_architecture.py
   uv run python scripts/validate_mcp_config.py
   uv run mypy src tests
   uv run pytest
   uv run bandit -c pyproject.toml -r src
   uv run pip-audit
   ```

3. If you changed a layer name or the allowed dependency direction in `template/docs/ARCHITECTURE.md`
   or `template/CLAUDE.md`, update `LAYERS`/`FORBIDDEN_LOCAL`/`FORBIDDEN_EXTERNAL` in
   `template/scripts/validate_architecture.py` to match - the validator is what actually enforces the
   rule, not the prose.
4. If you changed engineering standards in `template/CLAUDE.md`, check whether a path-scoped file
   under `template/.claude/rules/` elaborates that same section and needs the matching update.

## Changing `plugin/python-engineering-harness/`

1. Agents and skills are copied close to as-is from `template/.claude/`; hook scripts live under
   `plugin/python-engineering-harness/scripts/` and reference `${CLAUDE_PLUGIN_ROOT}` instead of
   `${CLAUDE_PROJECT_DIR}`. When you change a hook's behavior in one tree, port the equivalent change
   to the other.
2. Validate:

   ```bash
   python3 -m py_compile plugin/python-engineering-harness/scripts/*.py
   claude plugin validate ./plugin/python-engineering-harness
   claude --plugin-dir ./plugin/python-engineering-harness
   ```

   `claude plugin validate` requires the Claude Code CLI; if it isn't available in your environment,
   say so explicitly rather than reporting the plugin as validated.

## Keeping the two trees in sync

A change to engineering standards or hook behavior generally needs to land in both `template/` and
`plugin/python-engineering-harness/`. Before opening a PR, diff the two agent/skill directories for
the files you touched and confirm the divergence is only the expected one (path-token substitution,
`${CLAUDE_PLUGIN_ROOT}` vs. `${CLAUDE_PROJECT_DIR}`).

## Versioning and changelog

- Add an entry to `CHANGELOG.md` under `Added`/`Changed`/`Security` as appropriate. Explain *why* a
  change was made, not just what changed - future contributors and `SOURCES.md` reviews rely on that
  reasoning.
- If the change affects the plugin, bump `version` in
  `plugin/python-engineering-harness/.claude-plugin/plugin.json` and in `.claude-plugin/marketplace.json`
  together, and keep both equal to the `CHANGELOG.md` heading you added.
- If a change to `template/` or the bootstrapped project's behavior means an already-bootstrapped
  repository needs to do something to adopt it (not just re-render), add a migration note - see
  `docs/UPGRADING.md`.
- Update `VALIDATION.md` when you actually exercise something new (a rendering path, a hook case, a
  quality-gate step) or when previously environment-dependent coverage becomes exercisable. Don't
  claim a check passed if you didn't run it in this pass.
- If a design choice is grounded in a specific piece of official Claude Code, uv, or Ruff
  documentation, add the source URL and review date to `SOURCES.md`.

## Documentation language

English is canonical for all documentation and code. Repo-root docs (`README.md`, `SOURCES.md`,
`VALIDATION.md`, `CONTRIBUTING.md`, `SECURITY.md`, `docs/ENTERPRISE_ROLLOUT.md`, `docs/UPGRADING.md`)
additionally ship a `<name>.pt-BR.md` sibling, cross-linked at the top of both files. `CHANGELOG.md`
and everything under `template/`/`plugin/` (code, rules, agents, skills) stay English-only. When you
edit a file that has a `.pt-BR.md` sibling, update both in the same PR - the translation should not
drift from the English original.

## Pull request checklist

- [ ] Changed `template/` and `plugin/` together where the change is meant to apply to both.
- [ ] Rendered `template/` (or ran `claude plugin validate`) and reported the actual result, not an
      assumed one.
- [ ] Updated `CHANGELOG.md`, and `VALIDATION.md` if validation coverage changed.
- [ ] Bumped plugin/marketplace `version` fields together if the plugin changed.
- [ ] Updated the matching `.pt-BR.md` sibling for any repo-root doc you touched.
- [ ] Added a migration note to `docs/UPGRADING.md` if existing bootstrapped repositories need to do
      something beyond re-rendering to pick up the change.
