# Security policy

This repository distributes security-sensitive hooks, validators, MCP guardrails, and quality-gate
configuration. Vulnerabilities in the harness itself should be reported privately.

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

Until a dedicated security contact is published:

- On GitHub, use **Security** -> **Report a vulnerability**.
- Otherwise, contact the owner defined in `docs/ENTERPRISE_ROLLOUT.md` through a private internal
  channel.

Please do not open a public issue for a suspected vulnerability before the maintainers have had a
chance to assess and, where warranted, ship a fix.

## What to include

- The affected hook, validator, or bootstrap option and a minimal reproduction.
- Whether the issue reproduces against `template/`, `plugin/python-engineering-harness/`, or both.
- Claude Code version and operating system when hook or shell behavior is involved.

Allow maintainers time to assess the report and publish a fix with release notes before public
disclosure. A bypass can propagate to every project generated from an affected version.
