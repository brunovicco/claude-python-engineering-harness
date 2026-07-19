# Versioning model

This repository contains three independently versioned artifacts:

| Artifact | Current version source | Meaning |
|---|---|---|
| Harness generator | `bootstrap.py` (`HARNESS_VERSION`) | Version recorded in generated project metadata (`.harness.json`) and used for upgrade and drift checks. |
| Development package | root `pyproject.toml` | Local tooling package for developing and validating this repository; it is not the generated project's version. |
| Claude Code plugin | `plugin/python-engineering-harness/.claude-plugin/plugin.json` | Installable plugin release containing reusable agents, skills, hooks, and output style. The repository marketplace (`.claude-plugin/marketplace.json`) tracks the plugin version it distributes. |

Versions do not need to match. A generator release can change templates without changing the
plugin, and a plugin release can improve workflows without changing generated files. Each artifact
uses semantic versioning within its own lifecycle.

The generated project's version is separately owned by that project and starts at `0.1.0` by
default. Upgrading the harness must never overwrite that application or library version.

Release notes must identify which artifact changed. Compatibility-impacting changes to generated
files require a harness version change and upgrade instructions. Plugin-only changes require a
plugin version change. The root development package changes only when its packaging contract
changes.

Git tags (`vX.Y.Z`) follow the harness generator version. The sibling
`codex-python-engineering-harness` and any cross-harness tooling consume this repository by
release tag, so every compatibility-impacting generator change must be tagged.
