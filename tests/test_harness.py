"""Regression tests for bootstrap, validators, hooks, and distribution parity."""

import ast
import compileall
import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any

import bootstrap

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "template" / ".claude" / "hooks"
PLUGIN_SCRIPTS = ROOT / "plugin" / "python-engineering-harness" / "scripts"
VALUES = {
    "project_name": "test-service",
    "package_name": "test_service",
    "python_version": "3.13",
    "ruff_target_version": "py313",
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


class ValidatorTests(unittest.TestCase):
    """Exercise architecture and MCP policy regressions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.architecture = load_module(
            "harness_validate_architecture",
            ROOT / "template" / "scripts" / "validate_architecture.py",
        )
        cls.mcp = load_module(
            "harness_validate_mcp", ROOT / "template" / "scripts" / "validate_mcp_config.py"
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


if __name__ == "__main__":
    unittest.main()
