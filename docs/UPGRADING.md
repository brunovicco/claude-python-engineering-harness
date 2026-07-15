# Upgrading a bootstrapped project

*[Português](UPGRADING.pt-BR.md)*

The harness can safely merge files into an existing repository, but it does not record which
harness version created that repository. Record the source tag or commit in each project's README
or provisioning configuration before performing future upgrades.

## Procedure

1. Read `CHANGELOG.md` from the project's recorded version to the target version.
2. Apply the current template without overwriting existing files:

   ```bash
   python3 bootstrap.py --name <existing-project> --package <existing_package> \
     --target /path/to/existing-repo --merge
   ```

3. Review every generated `.harness-new` file. If that name exists, bootstrap uses a numbered
   suffix such as `.harness-new.2`.
4. Adopt harness fixes, preserve intentional project customizations, and manually reconcile files
   changed on both sides. Delete resolved conflict files.
5. Run the project's complete quality gate and update its recorded harness version.

If no source version was recorded, compare against the latest harness and treat every difference as
a manual migration decision.

## Files requiring careful review

- `.claude/hooks/` and plugin hook scripts carry enforcement logic and usually should be updated.
- `scripts/validate_architecture.py` must retain project-specific layers and dependency rules.
- `.claude/settings.json` permissions are project-specific and should be reconciled, not replaced.
- `CLAUDE.md` and `AGENTS.md` combine shared standards with project facts and require a manual merge.
- Agent and skill frontmatter additions are not applied retroactively unless their new file is
  adopted.

For a portfolio of repositories, upgrade a low-risk pilot first, verify hook and quality-gate
behavior, and then reuse the reviewed migration decisions. See `ENTERPRISE_ROLLOUT.md` for rollout,
ownership, and rollback guidance.
