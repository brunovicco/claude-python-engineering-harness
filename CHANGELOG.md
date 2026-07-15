# Changelog

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
