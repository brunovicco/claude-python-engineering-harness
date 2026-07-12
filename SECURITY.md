# Security policy

*[Português](SECURITY.pt-BR.md)*

This repository distributes the security-sensitive parts of a Claude Code setup: hooks that block
destructive commands and sensitive-file access, secret-shaped-content scanning, MCP governance
guardrails, and a Bandit/pip-audit-backed quality gate for generated projects. Treat vulnerabilities
in this repository - not just in the applications it scaffolds - as security issues worth reporting
responsibly.

## What is in scope

- Bypasses of the `PreToolUse`/`PostToolUse` hooks under `template/.claude/hooks/` and
  `plugin/python-engineering-harness/scripts/` (`protect_sensitive_files.py`, `validate_bash.py`,
  `guard_mcp.py`, `scan_secrets.py`) - e.g. a destructive command pattern, a sensitive path, or a
  secret shape that should be blocked but isn't.
- Logic errors in `template/scripts/validate_architecture.py` or
  `template/scripts/validate_mcp_config.py` that let a violating configuration or dependency pass
  the gate.
- `bootstrap.py` behavior that could write outside the intended target directory, clobber files
  under `--merge` in a way the documented `.harness-new` conflict path does not describe, or
  otherwise defeat the "never overwrite existing files" guarantee.
- MCP governance gaps: anything that would let a configured server exfiltrate secrets past
  `guard_mcp.py`, or that would let a state-mutating tool call skip the confirmation requirement
  documented in `template/docs/MCP.md`.
- Any documented control in `docs/ENTERPRISE_ROLLOUT.md` (allowlist/denylist enforcement, managed
  settings examples) that does not behave as described.

## What is out of scope

- Vulnerabilities in third-party dependencies pulled into a *bootstrapped* project (`fastapi`,
  `sqlalchemy`, etc.) - report those upstream; `pip-audit` in the generated project's quality gate is
  the intended detection mechanism, not this policy.
- Findings that require the operator to have already disabled a documented safety control (for
  example, an explicitly-approved `bypassPermissions` mode, or a hand-edited hook that removes a
  check) - the harness's threat model assumes its shipped controls are left in place.
- Issues in Claude Code itself, as opposed to this harness's configuration of it - report those to
  Anthropic through the official Claude Code channels.

## Reporting a vulnerability

This project does not yet publish a dedicated security contact address. Until one is added here:

- If this repository is hosted on GitHub, use GitHub's private vulnerability reporting
  (**Security** tab -> **Report a vulnerability**) so the report is not publicly visible before a
  fix ships.
- Otherwise, contact the repository owner listed under "Recommended ownership" in
  `docs/ENTERPRISE_ROLLOUT.md` (platform engineering for hooks and CI baseline, security for blocked
  paths and secret patterns) through your organization's internal channel.

Please do not open a public issue for a suspected vulnerability before the maintainers have had a
chance to assess and, where warranted, ship a fix.

## What to include

- The specific hook, script, or bootstrap flag involved, and the exact input or command that should
  have been blocked and was not (or that produced unexpected write behavior).
- Whether the issue reproduces against `template/`, `plugin/python-engineering-harness/`, or both.
- Your Claude Code version and OS, since hook matching and shell behavior can differ across
  platforms (`template/README.md` and this repo's `README.md` both note macOS/Linux/WSL as the
  supported set for the default hook configuration).

## Disclosure

Given this is a template/plugin distribution rather than a hosted service, there is no user data to
protect directly, but a missed hook bypass or gate failure could propagate into every project that
bootstraps from an affected version. Please allow time for a fix and a `CHANGELOG.md` entry (see the
`Security` section convention already used there) before public disclosure.
