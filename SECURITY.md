# Security policy

This repository distributes security-sensitive hooks, validators, MCP guardrails, and quality-gate
configuration. Vulnerabilities in the harness itself should be reported privately.

## Supported versions

Security fixes are provided for the latest release on the default branch. Older releases and
generated projects are not patched in place; upgrade them to the latest harness release and review
the migration notes in `docs/UPGRADING.md`.

## What is in scope

- Bypasses of hooks under `template/.claude/hooks/` or plugin `scripts/`, including destructive
  commands, sensitive paths, secret scanning, or MCP confirmation and exfiltration controls.
- Architecture or MCP validator errors that allow prohibited dependencies or configurations.
- Bootstrap writes outside the target, unexpected overwrites, symlink escapes, or broken `--merge`
  conflict handling.
- Managed-policy examples in `docs/ENTERPRISE_ROLLOUT.md` that do not enforce the stated behavior.

## What is out of scope

- Third-party dependency vulnerabilities in a generated project; report them upstream.
- Findings that require an operator to have disabled or removed a documented safety control.
- Issues in Claude Code itself rather than this repository's configuration.

## Reporting a vulnerability

- Prefer GitHub's private vulnerability reporting: open the repository's **Security** tab and choose
  **Report a vulnerability**.
- If that option is unavailable, email **bfvicco@gmail.com** with the subject
  `[SECURITY] claude-python-engineering-harness`. Do not include production secrets or personal data
  that are not needed to reproduce the issue.

Please do not open a public issue for a suspected vulnerability before the maintainers have had a
chance to assess and, where warranted, ship a fix.

## What to include

- The affected hook, validator, or bootstrap option and a minimal reproduction.
- Whether the issue reproduces against `template/`, `plugin/python-engineering-harness/`, or both.
- Claude Code version and operating system when hook or shell behavior is involved.

You should receive an acknowledgement within five business days. The initial response will confirm
the scope, severity triage, and the next update date; remediation time depends on impact and release
complexity. Coordinate public disclosure with the maintainer. A bypass can propagate to every
project generated from an affected version.
