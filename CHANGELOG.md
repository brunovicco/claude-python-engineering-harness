# Changelog

All notable changes to the harness are documented here. Harness, development package, and plugin
versions are independent; see `docs/VERSIONING.md`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the harness uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **Generated-project change.** `.claude/settings.json` enables Claude Code's Bash sandbox:
  `enabled: true`, `allowUnsandboxedCommands: false` (no unsandboxed retry), and
  `autoAllowBashIfSandboxed: false` so approval prompts are unchanged. Writes are limited to the
  project plus the uv and pip-audit caches, network to `pypi.org` and `files.pythonhosted.org`
  without a prompt, and the existing `Read` deny rules also deny those reads to commands. Hooks
  stay as defense in depth. See the generated `docs/DEVELOPMENT.md`.
- `validate_bash.py` (template and plugin) now inspects the unquoted form of a command and the
  payload of `bash`/`sh`/`zsh`/`dash`/`ksh -c` and `eval` (up to three levels), expands brace groups,
  and matches shell globs against sensitive names with shell dotfile semantics. This blocks
  evasions such as `git reset --ha""rd`, `bash -c '...'`, `cat ./.e?v`, `cat .e*`, `cat .[e]nv`,
  and `cat .{e,x}nv`, while `ls *`, `rm -f *.pyc`, and `cp pyproject.toml{,.bak}` stay allowed.
  `git push origin +main` (force-push refspec) is now blocked.
- Re-vendored the loop-contract validator from `engineering-loop-schemas` v0.3.0
  (`5340d491b46f4fabc967c81bb3e5204104b6b5d8`). The previously vendored v0.1.2 validator accepted
  contracts with unknown properties, arbitrary `version` values, and report-only contracts with
  `human_review.required: false`; v0.3.0 enforces the canonical JSON Schema and rejects all three.
  Valid existing contracts remain valid (contract wire format stays `1.0.0`).
- `validate_loop_schema_vendor.py` now verifies manifest format `2.0.0`: the size and SHA-256 of
  every Python source and of the four canonical JSON Schemas, every declared import adaptation,
  and the absence of any file the manifest does not declare (for example a planted module).
- Refreshed vulnerable development-only transitive dependencies in `uv.lock`, which made the
  repository `pip-audit` check (and therefore the `repository-quality` job on `main`) fail:
  `certifi` 2026.10.23, `filelock` 4.2.12, `msgpack` 1.2.4, `pip` 26.3, and `urllib3` 2.8.0. All
  are pulled in by `pip-audit`; no runtime dependency of generated projects changes.
- Pinned `actions/checkout` to a full commit SHA in every distributed workflow (`template/` and
  `profiles/`), and updated the distributed `astral-sh/setup-uv` pin from v8.1.0 to v10.3.3.
  Generated projects previously received an outdated `setup-uv` and, where a tag was used, a
  mutable action reference.

### Fixed

- The low-level disk rule never matched `dd if=/dev/...`: its trailing word boundary required a
  word character after `if=`. It now blocks `dd if=` as intended.
- The CI step that validates `template/.claude/workflows/review-branch.js` used `node --check`,
  which is not a faithful parser for Claude Code workflow files: they run as the body of an async
  function (top-level `await` and `return`). Newer Node versions on the current GitHub runner
  image detect the file as an ES module and reject the top-level `return`, failing every `test`
  job. The step now compiles each workflow body as an `AsyncFunction`, which matches how the
  file actually runs and still rejects real syntax errors.

### Changed

- Added `tests/adversarial/bash_hook_corpus.json`, a corpus shared byte-for-byte with the sibling
  harness and listed in `parity-manifest.json`: regression and evasion cases the hook must deny,
  benign commands it must allow, and known bypasses that each name the control covering them. Every
  distributed copy of the hook runs against it; a known bypass that starts being blocked fails the
  test so it is promoted to a protected case.
- **Generated-project change; harness generator 1.1.0.** The Evidence-Gated Engineering Loop layer
  (`scripts/_vendor_loop_schemas/`, `validate_loop_contracts.py`, `validate_loop_schema_vendor.py`
  and their quality-gate checks) is now opt-in through `bootstrap.py --loop` instead of being
  rendered into every project, where it was a no-op unless a human added a contract. The selection
  is recorded as `loop` in `.harness.json`; `--merge` keeps it, and a project rendered before this
  change that tracks the vendored bundle keeps the layer. `--no-loop` disables it and lists the
  files left in place. A contract under `.loop/contracts/` without the layer fails both the
  generated quality gate and `bootstrap.py --check`. See `docs/LOOPS.md` and `docs/UPGRADING.md`.
- The repository quality gate, the self-evaluation workflow, and the CI generated-profiles matrix
  render the loop layer (with the agentic governance profile, and on every profile and Python
  version, respectively), while the `none` case keeps covering the default render.
- Repository mypy treats the vendored bundle as third-party code (`ignore_errors` for
  `_vendor_loop_schemas.*`): mypy 2.4 reports redundant casts in it that belong upstream, and the
  bundle is integrity-verified and must not be edited locally.
- The isolated lint in the `test` job now reads the ruff version from `uv.lock` instead of a
  hard-coded `ruff==0.15.20`, so it can never drift from the version the repository quality gate
  uses, and Dependabot updates both together. Its rule set is pinned to `E4,E7,E9,F`, the set it
  enforced before: `--isolated` ignores project config, and ruff 0.17 expanded its default
  selection from 59 to 407 rules, which would otherwise change the check under every update.
- Updated the harness CI actions: `actions/checkout` v7.0.1, `actions/setup-python` v7.1.0,
  `astral-sh/setup-uv` v10.3.3, and `actions/upload-artifact` v7.0.2, all pinned to full commit
  SHAs verified against their release tags. The only inputs used (`python-version`, `version`)
  are unchanged across these major versions. Supersedes the open Dependabot pull requests.
- `.github/dependabot.yml` is now identical in shape across the sibling harnesses: weekly grouped
  updates for GitHub Actions in the repository *and* in the distributed `template/` and `profiles/`
  workflows, for the `uv` lockfile (previously not covered at all, so lockfile
  vulnerabilities never produced update PRs), and for the template container images.
- Added regression tests that require every workflow action, including distributed ones, to be
  pinned to a full commit SHA with a version comment, and that keep Dependabot pointed at every
  distributed workflow directory.

### Added

- README "Five-minute evaluation" section, matching the sibling
  `codex-python-engineering-harness`: a disposable, credential-free local evaluation with a
  single quality-gate command, plus explicit use / do-not-use guidance.

## 1.0.0 - 2026-07-19

First tagged release. Consolidates the loop foundation below and closes the structural-parity gap
with the sibling `codex-python-engineering-harness` (which consumes releases by tag).

### Added

- Repository-level `pyproject.toml`, `uv.lock`, and `scripts/quality_gate.py`, so the harness runs
  the same deterministic gate it installs into generated projects (Ruff, format, Mypy, Bandit,
  pip-audit, regression tests, governance gate, and the full profile × governance render matrix)
  on its own code. A new `repository-quality` CI job invokes it.
- `docs/ARCHITECTURE.md` (Claude-native surface decisions, profile and governance composition,
  and the documented Langfuse-vs-OpenTelemetry divergence from the Codex sibling) and
  `docs/VERSIONING.md` (independent harness, development package, and plugin lifecycles).
- `scripts/parity_check.py` with `parity-manifest.json` and `parity-exceptions.json`: a
  deterministic check, shared with the Codex sibling, that fails CI when a parity-required
  artifact is missing and is not declared as an intentional divergence. Wired into CI.
- A documented language policy in `CONTRIBUTING.md` (English canonical; pt-BR required for
  `docs/LOOPS`, `docs/UPGRADING`, and `docs/ENTERPRISE_ROLLOUT`).

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

### Changed

- Harness, plugin, and marketplace versions promoted from 0.6.0 to 1.0.0.

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
