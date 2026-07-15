# Upgrading a bootstrapped project

*[Português](UPGRADING.pt-BR.md)*

Harness 0.5.0 and later records the version, profile, Python version, source state, generated-file
hashes, and file modes in `.harness.json`. Older projects have no baseline, so their first upgrade
remains a manual reconciliation.

## Procedure

1. Read `CHANGELOG.md` from the project's recorded version to the target version.
2. Apply the current template without overwriting existing files:

   ```bash
   python3 bootstrap.py --name <existing-project> --package <existing_package> \
     --target /path/to/existing-repo --merge
   ```

3. The bootstrap automatically updates files whose current hash matches the prior manifest. Review
   every generated `.harness-new` file. If that name exists, bootstrap uses a numbered
   suffix such as `.harness-new.2`.
4. Adopt harness fixes, preserve intentional project customizations, and manually reconcile files
   changed on both sides. Delete resolved conflict files.
5. Run `python3 bootstrap.py --target /path/to/existing-repo --check`, then run the project's
   `scripts/quality_gate.py`. The bootstrap updates the recorded version after rendering.

If no source version was recorded, compare against the latest harness and treat every difference as
a manual migration decision.

## Files requiring careful review

- `.claude/hooks/` and plugin hook scripts carry enforcement logic and usually should be updated.
- Architecture-specific roots and boundaries belong in `pyproject.toml`; keep the generic validator
  executable in sync with the harness.
- `.claude/settings.json` permissions are project-specific and should be reconciled, not replaced.
- `CLAUDE.md` and `AGENTS.md` combine shared standards with project facts and require a manual merge.
- Agent and skill frontmatter additions are not applied retroactively unless their new file is
  adopted.

For a portfolio of repositories, upgrade a low-risk pilot first, verify hook and quality-gate
behavior, and then reuse the reviewed migration decisions. See `ENTERPRISE_ROLLOUT.md` for rollout,
ownership, and rollback guidance.
