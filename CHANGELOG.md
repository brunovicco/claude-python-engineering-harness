# Changelog

## 0.3.0 - 2026-07-11

### Added

- `log_event` and `block_action` helpers in `.claude/hooks/_common.py` (and the plugin's
  `scripts/_common.py`): every PreToolUse deny/ask and the PostToolUse secret-scan block now
  append a structured line (timestamp, hook, category, decision, tool name - never command text,
  file contents, or matched values) to `.claude/logs/hooks-audit.jsonl`. This operationalizes the
  "hook denials by category" metric `docs/ENTERPRISE_ROLLOUT.md` already documented as a rollout
  goal but that no hook previously recorded anywhere durable.
- `memory: project` on the `debugger` agent, so recurring root causes, environment quirks, and
  flaky-test signatures persist across sessions under `.claude/agent-memory/debugger/` instead of
  being re-derived every investigation.
- Documented, opt-in `isolation: worktree` pattern for `python-implementer` (`docs/DEVELOPMENT.md`,
  `README.md`) for larger or harder-to-reverse changes.
- `entrypoints/logging.py` in the generated project: a real structlog/stdlib bootstrap
  (`configure_logging`, `bind_correlation_id`, `clear_request_context`) implementing what
  `.claude/rules/observability.md` already required but no code previously configured. JSON to
  stdout by default; `LOG_FORMAT=console` for local development.
- `adapters/tracing.py`: an opt-in Langfuse observer for LLM call metadata (latency, tokens, model).
  `build_llm_call_observer()` returns a no-op observer unless the new `tracing` optional dependency
  group is installed and Langfuse credentials are set. Prompt/completion content is withheld unless
  `LANGFUSE_CAPTURE_CONTENT=true` is set after the approval checklist in the new
  `docs/LLM_OBSERVABILITY.md`, so it doesn't silently violate the existing "never log prompts or
  model responses" rule.
- `CONTRIBUTING.md`: how to change `template/` versus `plugin/python-engineering-harness/`, keep the
  two in sync, validate each, and the versioning/changelog/documentation-language conventions this
  repo already followed but had never written down for a new contributor.
- `SECURITY.md`: scope (hook bypasses, gate logic errors, `bootstrap.py` write guarantees, MCP
  governance gaps) and reporting process for vulnerabilities in the harness itself, as distinct from
  vulnerabilities in a bootstrapped project's own dependencies.
- `docs/UPGRADING.md`: the procedure for moving an already-bootstrapped repository to a newer harness
  version using the existing `--merge`/`.harness-new` mechanism, since neither `bootstrap.py` nor any
  other doc previously addressed re-applying the harness after the initial bootstrap. Documents
  explicitly that no version stamp is written into a bootstrapped project today, and recommends
  tracking the harness version per repository until one is.

### Changed

- `scan_secrets.py` now emits its block decision through the shared `block_action` helper instead
  of building its own JSON, so all four PreToolUse/PostToolUse safety hooks funnel through the same
  audited output path.
- `.claude/rules/git-collaboration.md` now calls out reviewing `.claude/agent-memory/` diffs before
  committing, since that content is agent-written rather than human-authored.
- Plugin and marketplace version increased to 0.3.0.
- Removed `from __future__ import annotations` from every Python file in the repository (hooks,
  scripts, `bootstrap.py`, and the generated project's `src`/`tests`). It was a no-op given the
  Python 3.12 minimum `bootstrap.py` already enforces; `_FakeGeneration.__enter__` in
  `tests/unit/test_tracing.py` was the one real forward-reference case, now typed with
  `typing.Self` instead.
- Repo-root documentation (`README.md`, `SOURCES.md`, `VALIDATION.md`,
  `docs/ENTERPRISE_ROLLOUT.md`) is now bilingual: English is canonical, each file has a
  `<name>.pt-BR.md` sibling with a Portuguese translation and a language-switcher link at the top
  of both. `README.md` was previously Portuguese-only and is now the English version;
  `README.pt-BR.md` carries the original Portuguese content. `CHANGELOG.md` and everything under
  `template/`/`plugin/` stay English-only.

### Verification

Re-verified this harness's claims about Claude Code behavior against raw official documentation
markdown (not model-summarized fetches, which produced false positives on a first pass - see
`SOURCES.md`). Confirmed accurate and unchanged: hook matcher syntax (bare `|` is valid), `effort`
and `model: inherit` on subagents, `context: fork`/`agent:` on skills, `defaultEnabled` on plugins,
`category` on marketplace entries, `includeGitInstructions`/`respectGitignore`/
`disableBypassPermissionsMode` in `settings.json`, SSE deprecation, `serverUrl`/`serverCommand`
managed-MCP matching, and the `@AGENTS.md` import pattern in `CLAUDE.md`. No corrections were
needed to existing configuration.

Considered and deliberately not adopted: a `Stop`-event nudge to run the quality gate (fires after
every turn, not just end-of-task - too noisy for this harness's lean-context principle);
`SessionEnd`, `PreCompact`, `PostToolUseFailure`, `PermissionDenied`, and `UserPromptSubmit` hooks
(no concrete deterministic check in this harness's threat model maps to them; existing
`PreToolUse`/`PostToolUse` coverage already sits at the correct lifecycle point); and HTTP/prompt/
agent-type hook handlers (LLM-mediated hooks work against "instruction is not control" for anything
that must be guaranteed).

## 0.2.0 - 2026-07-08

### Added

- Opt-in MCP governance for Claude Code projects.
- `.mcp.json.example` with environment-based authentication references.
- `docs/MCP.md` covering transport, scope, authentication, prompt injection, permissions, data egress, and enterprise controls.
- Managed MCP and managed-settings examples.
- Path-scoped MCP engineering rules.
- `mcp-integrator` agent.
- `/configure-mcp` and `/review-mcp` skills.
- `guard_mcp.py` PreToolUse hook for secret exfiltration and external-state mutation controls.
- `validate_mcp_config.py` deterministic quality gate.
- MCP validation in CI and the standard quality-gate workflow.

### Changed

- Plugin and marketplace version increased to 0.2.0.
- Claude and engineering contracts now treat MCP results as untrusted external input.
- Enterprise rollout guidance now includes fixed managed server sets, allowlists, denylists, ownership, and telemetry.
- Bypass-permissions mode is disabled in the generated project settings.

### Security rationale

No generic MCP server is enabled by default. Integrations are opt-in because each server expands the trust boundary, data-egress surface, dependency chain, and set of external actions available to Claude Code.
