# Changelog

## [Unreleased]

### Added

- Phase 0-1 (report-only) Evidence-Gated Engineering Loop foundation, see `docs/LOOPS.md` /
  `docs/LOOPS.pt-BR.md`:
  - `.loop/**` and `scripts/loop_*` are now denylisted for agent writes in
    `protect_sensitive_files.py` (template and plugin), so an agent cannot silently build
    `loop_runner.py`/`loop_gate.py`/`loop_state.py` or populate `.loop/` ahead of schedule.
  - `template/scripts/_vendor_loop_schemas/` vendors the contract validator from
    `brunovicco/engineering-loop-schemas` (pinned commit recorded in each vendored file's
    header); `template/scripts/validate_loop_contracts.py` wires it into the generated
    project's quality gate as a new `loop-contracts` check that is a documented no-op until a
    human places a contract under `.loop/contracts/`.
  - `.github/workflows/loop-self-evaluation.yml` (`workflow_dispatch` + weekly schedule):
    renders every profile/governance-profile combination, gates each one, checks
    manifest/plugin/documentation consistency, and uploads a JSON + Markdown report as a build
    artifact. It never modifies repository code; its optional agent-interpretation step is
    disabled by default and defines no credentials. Minimal per-job permissions,
    `persist-credentials: false`, and full-SHA-pinned actions throughout.
  - The shared validator is now consumed as the deterministic `engineering-loop-schemas v0.1.2`
    bundle pinned to `0459d61b7b1d4e7b46709e6d3895770553e6fab0`. Its `manifest.json` records
    source provenance, file sizes, SHA-256 hashes, and the declared package-import adaptation.
    The mandatory `loop-schema-vendor` quality check validates the bundle offline, and regression
    tests prove that manual tampering is rejected. The earlier `75a63eef...` integration described
    below was an intermediate pre-release state and is superseded by this published bundle.

### Fixed

- Re-vendored `_vendor_loop_schemas/{__init__,models,validate_contract}.py` from
  `brunovicco/engineering-loop-schemas@75a63eef269fd995128ab39c89e551fe58a27bf7` before this
  was ever released, after the same fix caught a CI failure on the sibling Codex harness's
  generated-profiles Python 3.14 job: ruff's `UP037` flagged `models.py`'s load-bearing quoted
  self-referencing `from_dict` return annotations (e.g. `-> "Budgets"`) as removable, since it
  assumes PEP 649 lazy-annotation semantics whenever the caller's own `target-version` is
  `py314` -- wrong here, since the quotes are required on Python 3.12/3.13, which this file
  also has to support. Fixed via a `[tool.ruff.lint.per-file-ignores]` entry rather than an
  inline `# noqa` (an inline noqa becomes a *second* failure, `RUF100` unused-directive, on
  3.12/3.13, where `UP037` never fires); added the matching per-file-ignore to
  `template/pyproject.toml`, `profiles/library/pyproject.toml`, and
  `profiles/workspace/pyproject.toml` (the `service` profile has no override and inherits the
  template's). Also dropped a stray `# noqa: PLC0415` on `validate_contract.py`'s lazy
  `import yaml`, unused everywhere this vendors to (no consumer selects ruff's `PL` rules) and
  itself flagged by `RUF100` once `RUF` is enabled. Verified by rendering all three profiles at
  Python 3.12/3.13/3.14 and re-running the full test suite and `loop_self_evaluation.py`.

## 0.6.0 - 2026-07-16

### Added

- Opt-in `baseline`, `ai-assisted`, and `agentic` governance profiles, independently composable
  with DORA, ISO/IEC 42001, and NIST SP 800-53 overlays.
- A versioned canonical control catalog with crosswalks for NIST AI RMF, CIS Controls, MITRE ATLAS,
  OWASP LLM, and OWASP Agentic, plus schemas and project-owned governance records.
- A deterministic governance gate for control evidence, selected profiles, risks, and expiring
  exceptions, integrated into the generated project quality gate.

### Changed

- `.harness.json` now records the governance profile, overlays, and catalog version; governance
  remains disabled by default for backward-compatible project generation.
- Updated plugin and marketplace manifests to version 0.6.0.

## 0.5.0 - 2026-07-15

### Added

- Explicit `service`, `library`, and virtual-root `workspace` project profiles.
- `.harness.json` with version, profile, source state, generated-file hashes, and modes.
- Non-mutating `--dry-run` planning and `--check` consistency diagnostics.
- Configurable multi-root architecture discovery and default-deny package boundaries.

### Fixed

- Preserved customized files during upgrades while automatically updating unchanged generated files.

### Changed

- Pydantic, structlog, Docker, Clean Architecture, and Langfuse remain service-profile decisions;
  library and workspace projects do not inherit them.
- Added the Python 3.12-3.14 × profile CI matrix, including applicable Docker assertions.
- Removed postponed-annotation future imports and documented quoting only individual forward
  references when evaluation order requires it.

## 0.4.1 - 2026-07-15

### Added

- A project-owned `scripts/quality_gate.py` with named checks and configurable source/test roots.
- Regression coverage for branch alignment, safe sync permissions, project-owned quality commands,
  file modes, numbered conflicts, and symlink confinement.

### Fixed

- Initialized new repositories deterministically with `git init -b main` and tested CI alignment.
- Allowed safe `uv sync --frozen` argument variants in generated Claude Code permissions.
- Removed fixed `src tests` and `bandit -r src` assumptions from the plugin's primary path.

### Changed

- CI, project documentation, agents, and skills now call the same executable quality runner.

## 0.4.0 - 2026-07-15

### Added

- Repository-level regression tests and CI for Python 3.12-3.14.
- A `Stop` hook that scans all changed and untracked files for probable secrets.
- Bounded, allowlisted Langfuse metadata with backend-failure isolation.

### Fixed

- Made security hooks fail closed on malformed input and internal errors.
- Closed MCP mutation-classification, production-targeting, credential, and dependency-pinning gaps.
- Prevented bootstrap conflict overwrites, unsafe names and versions, and symlink path escapes.
- Preserved template file permissions during atomic rendering instead of making every hook
  executable with restrictive inherited modes.
- Detected outer-layer imports written as `from package import layer`.
- Constrained branch and file values passed to the parallel review workflow.
- Avoided treating inline jq `.env` property selectors as sensitive file access while continuing to
  block actual `.env` path arguments.

### Changed

- Consolidated entry documentation and reduced the always-loaded engineering contract; detailed
  guidance remains in path-scoped rules and specialized documents.
- Clarified that hooks are guardrails and that hard enforcement requires managed policy or sandboxing.
- Pinned the uv container image and corrected plugin installation guidance.
- Updated plugin and marketplace manifests to version 0.4.0.

## 0.3.0 - 2026-07-11

### Added

- Structured hook decision audit logs.
- Project memory for recurring debugger findings.
- Structured logging and optional metadata-only Langfuse tracing in generated projects.
- Contribution, security, upgrade, and enterprise rollout guidance.

### Changed

- Added an opt-in worktree isolation pattern for larger implementation tasks.
- Documented review of agent-written memory before commit.
- Published bilingual rollout and upgrade documentation.
- Updated plugin and marketplace manifests to version 0.3.0.

## 0.2.0 - 2026-07-08

### Added

- Opt-in MCP configuration, documentation, validation, review skills, and an integration agent.
- Guards for likely secret exfiltration and state-changing MCP tools.
- Managed MCP allowlist and fixed-server examples.

### Changed

- Disabled bypass-permissions mode in generated projects.
- Added MCP checks to the generated quality gate.
- Updated plugin and marketplace manifests to version 0.2.0.

MCP remains disabled by default because each server expands the trust boundary and data-egress
surface.
