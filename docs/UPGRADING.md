# Upgrading a bootstrapped project

*[Português](UPGRADING.pt-BR.md)*

`bootstrap.py` has one well-documented mode for a brand-new project (render everything) and one for
applying the harness to an existing repository without clobbering it (`--merge`). Neither mode
currently distinguishes "this repository has never seen the harness" from "this repository was
bootstrapped from an older harness version and needs to catch up." This document describes how to
handle the second case with what exists today, and calls out the gap explicitly rather than implying
a smoother path than the tooling actually provides.

## There is no version stamp in a bootstrapped project

`bootstrap.py` does not write a marker file recording which harness commit, tag, or `CHANGELOG.md`
version a project was rendered from. If you don't already track this yourself, you cannot ask the
tooling "what version am I on." Start doing so now if you maintain more than one bootstrapped
project:

- Record the harness commit hash or tag in the bootstrapped project's own `README.md` or in a
  comment where you invoked `bootstrap.py` (e.g. your provisioning script), and update it every time
  you re-apply the harness.
- If you maintain many bootstrapped repositories, track "harness version per repository" as you
  would any other shared-dependency version - the same way `docs/ENTERPRISE_ROLLOUT.md`'s "Metrics"
  section recommends tracking "repositories and developers on each harness version."

Without this, the best you can do is diff against the harness version you *believe* you started
from, or treat every upgrade as "compare against the latest harness and accept everything that looks
intentional."

## Upgrade procedure

1. **Read `CHANGELOG.md`** from your recorded starting version (or from the oldest entry, if
   untracked) to the version you're upgrading to. Each entry explains *why* a change was made -
   use that to judge whether it applies to your project (for example, a change scoped to MCP
   governance doesn't matter if you never enabled `.mcp.json`).
2. **Re-run bootstrap in `--merge` mode against your existing repository:**

   ```bash
   python3 bootstrap.py --name <existing-project> --package <existing_package> \
     --target /path/to/existing-repo --merge
   ```

   `--merge` never overwrites a file that already exists in the target. Every harness file that
   differs from what's already in your repository is written alongside the original with a
   `.harness-new` suffix instead.
3. **Review every `.harness-new` file individually.** For each one, decide whether the difference is:
   - a harness-side improvement you should adopt (replace your file, or hand-merge the parts that
     apply) - most `template/.claude/hooks/*.py`, `template/.claude/rules/*.md`, and
     `template/scripts/*.py` changes fall here, since they carry the actual enforcement logic;
   - a project-specific customization you made deliberately (keep your version, delete the
     `.harness-new` file) - this is expected for `AGENTS.md` run commands, `src/` package layout,
     `.claude/rules/architecture.md` layer names, and anything else `README.md`'s "Recommended
     customizations" list calls out as something you're meant to adjust per project;
   - a merge that needs manual reconciliation because both sides changed (rules files you've
     extended locally, or `.claude/settings.json` permission lists you've grown) - do this by hand,
     there's no three-way merge here.
4. **Delete the `.harness-new` files** once resolved; don't leave them checked in.
5. **Re-run the project's own quality gate** (`/quality-gate`, or the command sequence in
   `template/docs/DEVELOPMENT.md`) before merging the upgrade - a hook or validator change can
   surface a violation your project was previously passing silently (for example, a newly forbidden
   import in `validate_architecture.py`, or a newly required MCP config field).
6. **Update your version record** (see above) to the harness version you just merged.

## What usually needs the most attention

Based on the shape of past `CHANGELOG.md` entries, these categories are the ones most likely to
require action beyond a mechanical file replace:

- **Hook scripts** (`.claude/hooks/*.py` / plugin `scripts/*.py`): almost always safe to take
  wholesale, since they're stdlib-only and not meant to be project-customized - except
  `protect_sensitive_files.py`'s blocked-path list and `validate_bash.py`'s allow/deny patterns, if
  you've added project-specific entries.
- **`scripts/validate_architecture.py`**: if you've added your own layers or forbidden-dependency
  entries, hand-merge rather than replace.
- **`.claude/settings.json` permissions**: almost always project-specific; treat the harness version
  as a suggestion to reconcile against, not a replacement.
- **Agent/skill frontmatter fields** (`effort`, `memory`, `isolation`, `model`): new fields introduced
  in a harness upgrade (see `CHANGELOG.md` 0.3.0 for `memory: project` and `isolation: worktree` as
  examples) are opt-in and won't apply retroactively to your project's copies unless you take the
  `.harness-new` version.
- **`CLAUDE.md` / `AGENTS.md`**: these carry both harness-wide standards and project-specific facts
  in the same file, so a mechanical replace will erase your customizations - always hand-merge.

## If you maintain many bootstrapped projects

Treat this the same as any shared-dependency upgrade: upgrade a low-risk pilot project first,
confirm its quality gate and hook behavior are unaffected, then roll the same `.harness-new`
resolution decisions out to the rest. `docs/ENTERPRISE_ROLLOUT.md`'s change-governance section
describes what a harness release should carry (semantic version, release and migration notes, test
evidence, compatibility statement, rollback instructions) - use that checklist to decide whether a
given harness version is upgrade-worthy before you start.
