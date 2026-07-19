"""Regression tests for bootstrap, validators, hooks, and distribution parity."""

import ast
import compileall
import contextlib
import importlib.util
import io
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar

import bootstrap

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "template" / ".claude" / "hooks"
PLUGIN_SCRIPTS = ROOT / "plugin" / "python-engineering-harness" / "scripts"
VALUES = {
    "project_name": "test-service",
    "package_name": "test_service",
    "python_version": "3.13",
    "python_image_digest": bootstrap.PYTHON_IMAGE_DIGESTS["3.13"],
    "ruff_target_version": "py313",
    "profile": "service",
    "governance_profile": "none",
}


def load_module(name: str, path: Path) -> ModuleType:
    """Load a repository script as an isolated module."""
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def run_hook(
    script: str, payload: dict[str, Any] | str, cwd: Path
) -> subprocess.CompletedProcess[str]:
    """Run one project hook with a serialized Claude Code payload."""
    content = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOKS / script)],
        cwd=cwd,
        input=content,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


class BootstrapTests(unittest.TestCase):
    """Validate rendering input and non-destructive merge behavior."""

    def test_supported_python_versions_are_bounded(self) -> None:
        self.assertEqual(bootstrap.normalize_python_version("3.12"), ("3.12", "py312"))
        self.assertEqual(bootstrap.normalize_python_version("3.14"), ("3.14", "py314"))
        for invalid in ("3.11", "3.15", "3.013", "4.0"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                bootstrap.normalize_python_version(invalid)

    def test_supported_python_images_are_pinned_by_digest(self) -> None:
        self.assertEqual(
            set(bootstrap.PYTHON_IMAGE_DIGESTS),
            {f"3.{minor}" for minor in bootstrap.SUPPORTED_PYTHON_MINORS},
        )
        for digest in bootstrap.PYTHON_IMAGE_DIGESTS.values():
            self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")

    def test_python_keyword_is_not_a_package_name(self) -> None:
        with self.assertRaises(ValueError):
            bootstrap.validate_package_name("class")

    def test_project_name_cannot_break_rendered_configuration(self) -> None:
        for invalid in ("", ".hidden", "bad name", 'bad"name', "line\nbreak"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                bootstrap.validate_project_name(invalid)

    def test_merge_never_overwrites_an_existing_conflict_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template"
            target = root / "target"
            template.mkdir()
            target.mkdir()
            (template / "config.txt").write_text("new", encoding="utf-8")
            (target / "config.txt").write_text("old", encoding="utf-8")
            existing = target / "config.txt.harness-new"
            existing.write_text("keep", encoding="utf-8")

            conflicts = bootstrap.copy_template(template, target, VALUES, merge=True)

            self.assertEqual(existing.read_text(encoding="utf-8"), "keep")
            self.assertEqual(conflicts, [target / "config.txt.harness-new.2"])
            self.assertEqual(conflicts[0].read_text(encoding="utf-8"), "new")

    def test_merge_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template"
            target = root / "target"
            outside = root / "outside"
            (template / "nested").mkdir(parents=True)
            (template / "nested" / "file.txt").write_text("data", encoding="utf-8")
            target.mkdir()
            outside.mkdir()
            (target / "nested").symlink_to(outside, target_is_directory=True)

            with self.assertRaises(ValueError):
                bootstrap.copy_template(template, target, VALUES, merge=True)
            self.assertFalse((outside / "file.txt").exists())

    def test_render_preserves_template_file_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template"
            target = root / "target"
            template.mkdir()
            target.mkdir()
            executable = template / "executable.py"
            regular = template / "regular.py"
            executable.write_text("print('ok')\n", encoding="utf-8")
            regular.write_text("VALUE = 1\n", encoding="utf-8")
            executable.chmod(0o755)
            regular.chmod(0o644)

            bootstrap.copy_template(template, target, VALUES, merge=False)

            self.assertEqual(stat.S_IMODE((target / executable.name).stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE((target / regular.name).stat().st_mode), 0o644)

    def test_complete_template_renders_token_clean_and_compiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "rendered"
            target.mkdir()
            bootstrap.copy_template(ROOT / "template", target, VALUES, merge=False)
            unresolved = [
                path
                for path in target.rglob("*")
                if path.is_file()
                and b"{{" in path.read_bytes()
                and not path.name.endswith((".png", ".jpg"))
            ]
            self.assertEqual(unresolved, [])
            with (target / "pyproject.toml").open("rb") as handle:
                self.assertIsInstance(tomllib.load(handle), dict)
            self.assertTrue(compileall.compile_dir(target, quiet=1))

    def test_profiles_keep_service_default_and_avoid_artificial_workspace_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for profile in bootstrap.PROFILES:
                with self.subTest(profile=profile):
                    target = root / profile
                    result = bootstrap.main(
                        [
                            "--name",
                            f"sample-{profile}",
                            "--package",
                            f"sample_{profile}",
                            "--target",
                            str(target),
                            "--profile",
                            profile,
                        ]
                    )
                    self.assertEqual(result, 0)
                    manifest = json.loads((target / ".harness.json").read_text(encoding="utf-8"))
                    self.assertEqual(manifest["version"], bootstrap.HARNESS_VERSION)
                    self.assertEqual(manifest["profile"], profile)
                    self.assertEqual(manifest["governanceProfile"], "none")
                    self.assertEqual(manifest["governanceOverlays"], [])
                    self.assertIn("files", manifest)
                    self.assertTrue((target / "scripts" / "quality_gate.py").is_file())
                    self.assertFalse((target / "governance").exists())
                    self.assertTrue(compileall.compile_dir(target, quiet=1))

            service = root / "service"
            self.assertTrue((service / "Dockerfile").is_file())
            self.assertIn("structlog", (service / "pyproject.toml").read_text(encoding="utf-8"))

            library = root / "library"
            self.assertFalse((library / "Dockerfile").exists())
            library_project = (library / "pyproject.toml").read_text(encoding="utf-8")
            self.assertNotIn("pydantic", library_project)
            self.assertNotIn("structlog", library_project)
            self.assertNotIn("langfuse", library_project)
            library_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in library.rglob("*")
                if path.is_file() and path.suffix in {".json", ".md", ".toml", ".yml"}
            ).lower()
            self.assertNotIn("langfuse", library_text)
            self.assertNotIn("mypy src tests", library_text)
            self.assertNotIn("bandit -c pyproject.toml -r src", library_text)

            workspace = root / "workspace"
            self.assertFalse((workspace / "Dockerfile").exists())
            self.assertFalse((workspace / "src").exists())
            self.assertFalse((workspace / "tests").exists())
            with (workspace / "pyproject.toml").open("rb") as handle:
                project = tomllib.load(handle)
            self.assertFalse(project["tool"]["uv"]["package"])
            self.assertNotIn("build-system", project)
            workspace_text = "\n".join(
                path.read_text(encoding="utf-8")
                for path in workspace.rglob("*")
                if path.is_file() and path.suffix in {".json", ".md", ".toml", ".yml"}
            ).lower()
            self.assertNotIn("langfuse", workspace_text)
            self.assertNotIn("mypy src tests", workspace_text)

    def test_governance_profiles_and_overlays_render_versioned_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for governance_profile in bootstrap.GOVERNANCE_PROFILES[1:]:
                with self.subTest(governance_profile=governance_profile):
                    target = root / governance_profile
                    arguments = [
                        "--name",
                        f"sample-{governance_profile}",
                        "--package",
                        f"sample_{governance_profile.replace('-', '_')}",
                        "--target",
                        str(target),
                        "--governance-profile",
                        governance_profile,
                    ]
                    if governance_profile == "agentic":
                        arguments.extend(
                            [
                                "--governance-overlay",
                                "dora",
                                "--governance-overlay",
                                "iso-iec-42001",
                            ]
                        )
                    self.assertEqual(bootstrap.main(arguments), 0)
                    manifest = json.loads((target / ".harness.json").read_text(encoding="utf-8"))
                    selection = json.loads(
                        (target / "governance/governance-profile.json").read_text(encoding="utf-8")
                    )
                    self.assertEqual(manifest["governanceProfile"], governance_profile)
                    self.assertEqual(
                        manifest["governanceCatalogVersion"],
                        bootstrap.GOVERNANCE_CATALOG_VERSION,
                    )
                    self.assertEqual(selection["name"], governance_profile)
                    required = selection["required_controls"]
                    self.assertEqual(len(required), len(set(required)))
                    self.assertTrue((target / "governance/control-catalog.json").is_file())
                    self.assertEqual(bootstrap.check_target(target), [])

            agentic = json.loads(
                (root / "agentic/governance/governance-profile.json").read_text(encoding="utf-8")
            )
            self.assertEqual(agentic["overlays"], ["dora", "iso-iec-42001"])
            self.assertEqual(agentic["framework_versions"]["dora"], "eu-2022-2554")
            self.assertIn("CPH-RES-001", agentic["required_controls"])

    def test_governance_overlay_requires_enabled_unique_profile(self) -> None:
        for arguments in (
            [
                "--name",
                "test",
                "--package",
                "test",
                "--target",
                "target",
                "--governance-overlay",
                "dora",
            ],
            [
                "--name",
                "test",
                "--package",
                "test",
                "--target",
                "target",
                "--governance-profile",
                "baseline",
                "--governance-overlay",
                "dora",
                "--governance-overlay",
                "dora",
            ],
        ):
            with self.subTest(arguments=arguments), self.assertRaises(SystemExit):
                bootstrap.parse_args(arguments)

    def test_git_init_uses_main_and_matches_generated_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            result = bootstrap.main(
                [
                    "--name",
                    "branch-test",
                    "--package",
                    "branch_test",
                    "--target",
                    str(target),
                    "--git-init",
                ]
            )
            self.assertEqual(result, 0)
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(branch, "main")
            self.assertIn(
                branch, bootstrap._workflow_branches(target / ".github/workflows/quality.yml")
            )
            self.assertEqual(bootstrap.check_target(target), [])

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = bootstrap.main(
                    [
                        "--name",
                        "dry-run",
                        "--package",
                        "dry_run",
                        "--target",
                        str(target),
                        "--dry-run",
                    ]
                )
            self.assertEqual(result, 0)
            self.assertFalse(target.exists())
            self.assertIn("NEW", output.getvalue())

    def test_dry_run_inspects_nonempty_target_without_merge_flag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            target.mkdir()
            (target / "README.md").write_text("custom", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = bootstrap.main(
                    [
                        "--name",
                        "dry-run",
                        "--package",
                        "dry_run",
                        "--target",
                        str(target),
                        "--dry-run",
                    ]
                )
            self.assertEqual(result, 1)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "custom")
            self.assertFalse((target / ".harness.json").exists())
            self.assertIn("CONFLICT README.md", output.getvalue())

    def test_manifest_hash_allows_safe_update_but_preserves_customization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            destination = target / "config.txt"
            destination.write_text("old", encoding="utf-8")
            previous = {"config.txt": {"sha256": bootstrap.sha256(b"old"), "mode": "0644"}}
            rendered = {Path("config.txt"): bootstrap.RenderedFile(b"new", 0o644)}

            changes = bootstrap.plan_changes(rendered, target, previous)
            self.assertEqual(changes[0].status, "update")
            bootstrap.apply_changes(changes, target, merge=True)
            self.assertEqual(destination.read_text(encoding="utf-8"), "new")

            destination.write_text("custom", encoding="utf-8")
            changes = bootstrap.plan_changes(rendered, target, previous)
            self.assertEqual(changes[0].status, "conflict")
            conflicts = bootstrap.apply_changes(changes, target, merge=True)
            self.assertEqual(destination.read_text(encoding="utf-8"), "custom")
            self.assertEqual(conflicts[0].read_text(encoding="utf-8"), "new")

    def test_check_detects_permission_drift_and_pending_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            self.assertEqual(
                bootstrap.main(
                    [
                        "--name",
                        "check-test",
                        "--package",
                        "check_test",
                        "--target",
                        str(target),
                    ]
                ),
                0,
            )
            gate = target / "scripts" / "quality_gate.py"
            gate.chmod(0o600)
            (target / "README.md.harness-new").write_text("pending", encoding="utf-8")
            errors = bootstrap.check_target(target)
            self.assertTrue(any("permission drift" in error for error in errors))
            self.assertTrue(any("pending conflict" in error for error in errors))

    def test_check_detects_version_tokens_ci_and_missing_documented_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            self.assertEqual(
                bootstrap.main(
                    [
                        "--name",
                        "audit-test",
                        "--package",
                        "audit_test",
                        "--target",
                        str(target),
                    ]
                ),
                0,
            )
            manifest_path = target / ".harness.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "0.4.0"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (target / "unrendered.txt").write_text("{{PROJECT_NAME}}", encoding="utf-8")
            workflow = target / ".github/workflows/quality.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace("branches: [main]", "branches: [dev]"),
                encoding="utf-8",
            )
            with (target / "AGENTS.md").open("a", encoding="utf-8") as handle:
                handle.write("\n`uv run python scripts/missing.py`\n")

            errors = bootstrap.check_target(target)
            self.assertTrue(any("harness version" in error for error in errors))
            self.assertTrue(any("unrendered token" in error for error in errors))
            self.assertTrue(any("CI branch mismatch" in error for error in errors))
            self.assertTrue(any("missing file" in error for error in errors))


class ValidatorTests(unittest.TestCase):
    """Exercise architecture and MCP policy regressions."""

    architecture: ClassVar[ModuleType]
    mcp: ClassVar[ModuleType]
    quality: ClassVar[ModuleType]
    governance: ClassVar[ModuleType]

    @classmethod
    def setUpClass(cls) -> None:
        cls.architecture = load_module(
            "harness_validate_architecture",
            ROOT / "template" / "scripts" / "validate_architecture.py",
        )
        cls.mcp = load_module(
            "harness_validate_mcp", ROOT / "template" / "scripts" / "validate_mcp_config.py"
        )
        cls.quality = load_module(
            "harness_quality_gate", ROOT / "template" / "scripts" / "quality_gate.py"
        )
        cls.governance = load_module(
            "harness_governance_gate", ROOT / "template" / "scripts" / "governance_gate.py"
        )

    def test_architecture_resolves_from_import_aliases(self) -> None:
        tree = ast.parse("from package import adapters\nfrom .. import entrypoints\n")
        imports = self.architecture.imported_modules(tree, ("package", "domain", "model"))
        self.assertEqual(imports, [(1, "package.adapters"), (2, "package.entrypoints")])

    def test_architecture_layer_ignores_package_name(self) -> None:
        self.assertEqual(self.architecture.layer_for(Path("domain/adapters/client.py")), "adapters")

    def test_architecture_blocks_from_import_of_outer_layer(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory) / "src"
            path = src / "package" / "domain" / "model.py"
            path.parent.mkdir(parents=True)
            path.write_text("from package import adapters\n", encoding="utf-8")
            violations = self.architecture.validate_file(path, src)
            self.assertEqual(len(violations), 1)
            self.assertIn("adapters", violations[0].message)

    def test_architecture_default_deny_boundary_reports_module_and_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "packages" / "core" / "src" / "core"
            package.mkdir(parents=True)
            path = package / "model.py"
            path.write_text(
                "import json\nimport requests\nimport importlib\nimportlib.import_module('x')\n",
                encoding="utf-8",
            )
            boundary = self.architecture.Boundary(package, ("stdlib", "core"), True)
            violations = self.architecture.validate_boundary_file(path, root, boundary)
            self.assertEqual([item.line for item in violations], [2, 4])
            self.assertTrue(all("core.model" in item.message for item in violations))

    def test_architecture_discovers_multiple_source_roots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("one", "two"):
                (root / "services" / name / "src").mkdir(parents=True)
            (root / "pyproject.toml").write_text(
                "[tool.engineering-harness.architecture]\n"
                'source-roots = ["services/*/src"]\n'
                "clean-architecture = false\n",
                encoding="utf-8",
            )
            roots, clean, boundaries = self.architecture.load_config(root)
            self.assertEqual(len(roots), 2)
            self.assertFalse(clean)
            self.assertEqual(boundaries, [])

    def test_quality_gate_keeps_named_checks_for_empty_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                "[tool.engineering-harness.quality]\n"
                'source-roots = ["packages/*/src"]\n'
                'test-roots = ["packages/*/tests"]\n',
                encoding="utf-8",
            )
            checks = {check.name: check.command for check in self.quality.configured_checks(root)}
            self.assertIn("governance", checks)
            self.assertIn("typing", checks)
            self.assertIn("security", checks)
            self.assertEqual(checks["typing"], ())
            self.assertEqual(checks["security"], ())

    def test_governance_source_catalog_is_valid(self) -> None:
        report, errors = self.governance.run_source(ROOT, None)
        self.assertEqual(errors, [])
        self.assertEqual(report["status"], "pass")
        self.assertGreater(report["control_count"], 0)

    def test_governance_gate_rejects_untreated_high_risk_and_expired_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            self.assertEqual(
                bootstrap.main(
                    [
                        "--name",
                        "governed-service",
                        "--package",
                        "governed_service",
                        "--target",
                        str(target),
                        "--governance-profile",
                        "agentic",
                    ]
                ),
                0,
            )
            (target / "governance/risks/risk-register.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "risks": [{"id": "RISK-001", "owner": "service-owner", "severity": "high"}],
                    }
                ),
                encoding="utf-8",
            )
            (target / "governance/exceptions.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "exceptions": [
                            {
                                "expires_on": "2000-01-01",
                                "id": "EXC-001",
                                "owner": "service-owner",
                                "status": "approved",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            report, errors = self.governance.run_generated(target, None)
            self.assertEqual(report["status"], "fail")
            self.assertTrue(any("formal decision" in error for error in errors))
            self.assertTrue(any("expired" in error for error in errors))

    def test_mcp_rejects_unpinned_runner_and_literal_secret_argument(self) -> None:
        config = {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "company-mcp@latest", "--token", "plain-secret"],
            "timeout": 60_000,
        }
        errors = self.mcp.validate_server(Path(".mcp.json"), "company", config)
        self.assertTrue(any("latest" in item for item in errors))
        self.assertTrue(any("sensitive argument" in item for item in errors))

    def test_mcp_rejects_unpinned_direct_uvx_package(self) -> None:
        config = {
            "type": "stdio",
            "command": "uvx",
            "args": ["company-mcp"],
            "timeout": 60_000,
        }
        errors = self.mcp.validate_server(Path(".mcp.json"), "company", config)
        self.assertTrue(any("exact == version" in item for item in errors))

    def test_mcp_rejects_url_credentials_and_mixed_sensitive_header(self) -> None:
        config = {
            "type": "http",
            "url": "https://user:password@example.com/mcp",
            "headers": {"Authorization": "hardcoded ${MCP_TOKEN}"},
            "timeout": 60_000,
        }
        errors = self.mcp.validate_server(Path(".mcp.json"), "company", config)
        self.assertTrue(any("user information" in item for item in errors))
        self.assertTrue(any("environment variable" in item for item in errors))


class HookTests(unittest.TestCase):
    """Verify fail-closed behavior and mutation classification."""

    def test_pre_tool_hook_fails_closed_on_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_hook("guard_mcp.py", "{", Path(directory))
        self.assertEqual(result.returncode, 2)
        self.assertIn("failed closed", result.stderr)

    def test_camel_case_mutation_requires_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "mcp__issues__createIssue",
                "tool_input": {"title": "test"},
            }
            result = run_hook("guard_mcp.py", payload, Path(directory))
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "ask")

    def test_production_mutation_is_denied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "mcp__issues__create_issue",
                "tool_input": {"environment": "production"},
            }
            result = run_hook("guard_mcp.py", payload, Path(directory))
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")

    def test_bash_blocks_sensitive_path_for_arbitrary_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -c 'open(\".env\").read()'"},
            }
            result = run_hook("validate_bash.py", payload, Path(directory))
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")

    def test_bash_allows_environment_example(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "Bash",
                "tool_input": {"command": "cat .env.example"},
            }
            result = run_hook("validate_bash.py", payload, Path(directory))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_bash_allows_jq_environment_property_selector(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "Bash",
                "tool_input": {"command": "jq -r '.env // {} | keys' ~/.claude/settings.json"},
            }
            result = run_hook("validate_bash.py", payload, Path(directory))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_bash_blocks_environment_file_used_as_jq_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "Bash",
                "tool_input": {"command": "jq -r '.' .env"},
            }
            result = run_hook("validate_bash.py", payload, Path(directory))
        decision = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")

    def test_protect_sensitive_files_blocks_out_of_scope_loop_paths(self) -> None:
        for target in (".loop/contracts/x.yaml", "scripts/loop_runner.py", "scripts/loop_gate.py"):
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as directory:
                    payload = {
                        "cwd": directory,
                        "tool_name": "Write",
                        "tool_input": {"file_path": target},
                    }
                    result = run_hook("protect_sensitive_files.py", payload, Path(directory))
                decision = json.loads(result.stdout)["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "deny")
                self.assertIn("out of scope", decision["permissionDecisionReason"])

    def test_protect_sensitive_files_allows_ordinary_scripts_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = {
                "cwd": directory,
                "tool_name": "Write",
                "tool_input": {"file_path": "scripts/validate_loop_contracts.py"},
            }
            result = run_hook("protect_sensitive_files.py", payload, Path(directory))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_stop_scan_finds_secret_written_outside_edit_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "generated.txt").write_text("AKIA1234567890ABCDEF\n", encoding="utf-8")
            payload = {"cwd": directory, "tool_name": "Stop", "tool_input": {}}
            result = run_hook("scan_worktree.py", payload, root)
        decision = json.loads(result.stdout)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("generated.txt", decision["reason"])

    def test_stop_scan_is_a_no_op_outside_git_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {"cwd": directory, "tool_name": "Stop", "tool_input": {}}
            result = run_hook("scan_worktree.py", payload, root)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")


class DistributionTests(unittest.TestCase):
    """Keep duplicated security code and machine-readable files valid."""

    def test_governance_json_documents_parse(self) -> None:
        paths = [
            *sorted((ROOT / "governance").rglob("*.json")),
            *sorted((ROOT / "template/governance").rglob("*.json")),
        ]
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_template_and_plugin_security_scripts_match(self) -> None:
        names = {path.name for path in HOOKS.glob("*.py")}
        self.assertEqual(names, {path.name for path in PLUGIN_SCRIPTS.glob("*.py")})
        for name in names:
            with self.subTest(name=name):
                self.assertEqual((HOOKS / name).read_bytes(), (PLUGIN_SCRIPTS / name).read_bytes())

    def test_json_manifests_and_settings_parse(self) -> None:
        paths = (
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / "plugin" / "python-engineering-harness" / ".claude-plugin" / "plugin.json",
            ROOT / "plugin" / "python-engineering-harness" / "hooks" / "hooks.json",
            ROOT / "template" / ".claude" / "settings.json",
            ROOT / "template" / ".mcp.json.example",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_plugin_and_marketplace_versions_match(self) -> None:
        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        plugin = json.loads(
            (
                ROOT / "plugin" / "python-engineering-harness" / ".claude-plugin" / "plugin.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["version"], plugin["version"])
        self.assertEqual(marketplace["plugins"][0]["version"], plugin["version"])

    def test_quality_plugin_prefers_project_runner_without_layout_assumption(self) -> None:
        paths = (
            ROOT / "plugin/python-engineering-harness/skills/quality-gate/SKILL.md",
            ROOT / "plugin/python-engineering-harness/agents/quality-verifier.md",
        )
        for path in paths:
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertIn("scripts/quality_gate.py", content)
                self.assertNotIn("mypy src tests", content)
                self.assertNotIn("bandit -c pyproject.toml -r src", content)

    def test_safe_frozen_sync_variants_are_allowed(self) -> None:
        settings = json.loads((ROOT / "template/.claude/settings.json").read_text(encoding="utf-8"))
        self.assertIn("Bash(uv sync --frozen *)", settings["permissions"]["allow"])

    def test_postponed_annotations_import_is_not_distributed(self) -> None:
        forbidden = "from __future__ import " + "annotations"
        offenders = [
            path.relative_to(ROOT)
            for path in ROOT.rglob("*.py")
            if ".venv" not in path.parts
            if forbidden in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])
        guidance = (ROOT / "template/.claude/rules/python.md").read_text(encoding="utf-8")
        self.assertIn(f"Do not use `{forbidden}`", guidance)


class LoopFoundationTests(unittest.TestCase):
    """Cover the Phase 0-1, report-only Evidence-Gated Engineering Loop foundation."""

    VALID_CONTRACT: ClassVar[dict[str, object]] = {
        "version": "1.0.0",
        "id": "example",
        "objective": "Example.",
        "trigger": {"type": "manual"},
        "selection": {"strategy": "single-issue"},
        "baseline": {"commands": ["true"]},
        "acceptance": {"hard_gates": ["lint"]},
        "budgets": {"max_tokens": 1000},
        "scope": {"allowlist": [], "denylist": []},
        "actions": {"allowed": [], "denied": []},
        "human_review": {"required": True},
    }

    @staticmethod
    def _stage_loop_scripts(root: Path) -> Path:
        """Copy the vendored validator into root/scripts/, as a generated project has it."""
        scripts_dir = root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            ROOT / "template/scripts/validate_loop_contracts.py",
            scripts_dir / "validate_loop_contracts.py",
        )
        shutil.copytree(
            ROOT / "template/scripts/_vendor_loop_schemas",
            scripts_dir / "_vendor_loop_schemas",
        )
        return scripts_dir / "validate_loop_contracts.py"

    def test_template_quality_gate_lists_loop_contracts_check(self) -> None:
        module = load_module("template_quality_gate", ROOT / "template/scripts/quality_gate.py")
        names = {check.name for check in module.configured_checks(ROOT / "template")}
        self.assertIn("loop-contracts", names)

    def test_vendored_loop_schemas_directory_does_not_match_its_own_denylist(self) -> None:
        """Regression guard: the vendored package must not self-block via scripts/loop_*."""
        vendor_dir = ROOT / "template/scripts/_vendor_loop_schemas"
        self.assertTrue(vendor_dir.is_dir())
        self.assertFalse(vendor_dir.name.startswith("loop_"))

    def test_validate_loop_contracts_skips_cleanly_with_no_contracts_dir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = self._stage_loop_scripts(root)
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skipping", result.stdout)

    def test_validate_loop_contracts_passes_a_valid_json_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = self._stage_loop_scripts(root)
            contracts_dir = root / ".loop" / "contracts"
            contracts_dir.mkdir(parents=True)
            (contracts_dir / "example.json").write_text(
                json.dumps(self.VALID_CONTRACT), encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid", result.stdout)

    def test_validate_loop_contracts_fails_an_invalid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = self._stage_loop_scripts(root)
            contracts_dir = root / ".loop" / "contracts"
            contracts_dir.mkdir(parents=True)
            (contracts_dir / "broken.json").write_text("{}", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Invalid loop contract", result.stderr)

    def test_loops_doc_exists_in_english_and_portuguese(self) -> None:
        self.assertTrue((ROOT / "docs/LOOPS.md").is_file())
        self.assertTrue((ROOT / "docs/LOOPS.pt-BR.md").is_file())


class SelfEvaluationWorkflowTests(unittest.TestCase):
    """Cover the report-only self-evaluation workflow (B3)."""

    def test_workflow_uses_minimal_pinned_and_credential_safe_actions(self) -> None:
        content = (ROOT / ".github/workflows/loop-self-evaluation.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", content)
        self.assertIn('cron: "0 7 * * 1"', content)
        self.assertIn("persist-credentials: false", content)
        self.assertNotIn("pull_request_target", content)
        self.assertRegex(content, r"permissions:\s*\{\}")
        self.assertIn("contents: read", content)
        mutable_action = re.compile(r"uses:\s+[^\s@]+@v\d+\s*$", re.MULTILINE)
        self.assertIsNone(mutable_action.search(content))

    def test_self_evaluation_report_is_generated_and_all_projects_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "report"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/loop_self_evaluation.py"),
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=900,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((output_dir / "report.json").read_text(encoding="utf-8"))
            markdown = (output_dir / "report.md").read_text(encoding="utf-8")
        self.assertTrue(report["manifest_and_docs_consistency"]["passed"])
        self.assertEqual(len(report["projects"]), 6)
        self.assertTrue(all(project["passed"] for project in report["projects"]))
        self.assertIn("report-only workflow", markdown)


if __name__ == "__main__":
    unittest.main()
