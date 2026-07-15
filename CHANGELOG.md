# Changelog

## 0.4.0 - 2026-07-15

### Added

- Repository-level regression tests and CI for Python 3.12-3.14.
- A `Stop` hook that scans all changed and untracked files for probable secrets.
- Bounded, allowlisted Langfuse metadata with backend-failure isolation.

### Fixed

- Made security hooks fail closed on malformed input and internal errors.
- Closed MCP mutation-classification, production-targeting, credential, and dependency-pinning gaps.
- Prevented bootstrap conflict overwrites, unsafe names and versions, and symlink path escapes.
- Detected outer-layer imports written as `from package import layer`.
- Constrained branch and file values passed to the parallel review workflow.

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
