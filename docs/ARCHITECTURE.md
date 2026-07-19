# Architecture decisions

## Claude Code-native surfaces

- `CLAUDE.md` is the always-loaded repository contract; `AGENTS.md` carries the shared
  cross-platform engineering contract so a generated project remains legible to non-Claude
  tooling. Generated profile overlays replace them only when commands and layout differ.
- Detailed guidance lives in path-scoped rules under `.claude/rules/`, loaded only when relevant
  files are touched, keeping the always-loaded contract small.
- Specialized subagents live in `.claude/agents/`; project skills in `.claude/skills/`.
  Distributable copies of both live at the plugin root (`plugin/python-engineering-harness/`).
- Hook scripts stay in `.claude/hooks/` so commands can resolve them from the Git root when
  Claude Code starts in a subdirectory. `.claude/settings.json` is the only project hook and
  permission representation at that layer.
- The plugin uses the documented default `hooks/hooks.json`; its commands resolve scripts through
  `CLAUDE_PLUGIN_ROOT` and its manifest does not duplicate the default hook path.
- The repo marketplace is `.claude-plugin/marketplace.json` and points to
  `./plugin/python-engineering-harness` relative to the marketplace root.

## Profile composition

`template/` is the service-compatible base. `library` removes service/container/observability
pieces and overlays library metadata. `workspace` removes all artificial package/test trees and
overlays a virtual uv root. Profiles are generator choices, never monorepo packages in this repo.

The `library` profile intentionally has no `.github/` overlay: it inherits the template's
workflow unchanged, because the project-owned `scripts/quality_gate.py` reads its roots from
`pyproject.toml` and needs no profile-specific CI. The `workspace` profile overrides the workflow
because member discovery changes the commands. (The Codex sibling ships a `library` CI overlay
because its template workflow differs; this asymmetry is declared in `parity-exceptions.json`.)

## Governance composition

Technical profiles and governance are orthogonal. `--governance-profile` selects capability-based
controls while repeatable `--governance-overlay` options add regulatory requirements. `none` is the
default to keep upgrades compatible. The bootstrap snapshots the canonical catalog, schemas, and
composed selection into each governed project; generated projects never depend on this source
repository at runtime.

The catalog uses original control descriptions and many-to-many support mappings. It does not copy
licensed standards or assert compliance. Project-owned inventories, risks, assessments, and
exceptions remain separate from bootstrap-owned snapshots.

## Controls

Lifecycle hooks provide defense in depth for command safety, sensitive paths, secret scanning,
MCP mutation classification, and changed-file formatting. They do not replace Claude Code
permission policy, sandboxing, CI, or human review. Hard enforcement requires managed policy,
credentials, and repository protection outside the agent's reach; hooks stop accidents and raise
the cost of drift.

## Observability divergence from the Codex sibling

The generated service's LLM-tracing starter uses Langfuse metadata-only tracing (`--extra
tracing`), while the Codex sibling ships an OpenTelemetry adapter (`--extra observability`). This
is an intentional platform-level decision, not drift: Codex exposes native OpenTelemetry export,
so its harness builds on that; Claude Code does not, so this harness offers an opt-in,
allowlisted-metadata Langfuse integration with backend-failure isolation instead. Both starters
collect metadata only — never prompts, completions, file contents, or command output. The
divergence is declared in `parity-exceptions.json`.
