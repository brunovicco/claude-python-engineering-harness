#!/usr/bin/env python3
"""Render the Claude Code Python harness into a target repository."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

TOKENS = {
    "{{PROJECT_NAME}}": "project_name",
    "{{PACKAGE_NAME}}": "package_name",
    "{{PYTHON_VERSION}}": "python_version",
    "{{RUFF_TARGET_VERSION}}": "ruff_target_version",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Project name, e.g. payments-api")
    parser.add_argument("--package", required=True, help="Python package, e.g. payments_api")
    parser.add_argument("--target", required=True, type=Path, help="Target repository")
    parser.add_argument("--python", default="3.13", dest="python_version")
    parser.add_argument("--merge", action="store_true", help="Preserve existing files")
    parser.add_argument("--git-init", action="store_true", help="Initialize a Git repository")
    parser.add_argument("--lock", action="store_true", help="Run uv lock after rendering")
    return parser.parse_args()


def normalize_python_version(value: str) -> tuple[str, str]:
    """Validate a Python version and return its version and Ruff target."""
    parts = value.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid Python version: {value!r}; expected MAJOR.MINOR")
    major, minor = (int(part) for part in parts)
    if major != 3 or minor < 12:
        raise ValueError("This harness supports Python 3.12 or newer.")
    return value, f"py{major}{minor}"


def validate_package_name(value: str) -> None:
    """Validate a Python package identifier."""
    if not value.isidentifier():
        raise ValueError(f"Invalid Python package name: {value!r}")


def render_text(content: str, values: dict[str, str]) -> str:
    """Replace scaffold tokens in text content."""
    for token, key in TOKENS.items():
        content = content.replace(token, values[key])
    return content


def destination_for(relative: Path, values: dict[str, str]) -> Path:
    """Render tokens embedded in a relative destination path."""
    parts = [render_text(part, values) for part in relative.parts]
    return Path(*parts)


def copy_template(template: Path, target: Path, values: dict[str, str], merge: bool) -> list[Path]:
    """Copy and render the template, preserving conflicts in merge mode."""
    conflicts: list[Path] = []
    for source in sorted(template.rglob("*")):
        relative = source.relative_to(template)
        destination = target / destination_for(relative, values)
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        try:
            rendered = render_text(data.decode("utf-8"), values).encode("utf-8")
        except UnicodeDecodeError:
            rendered = data

        if destination.exists() and merge:
            if destination.read_bytes() == rendered:
                continue
            candidate = destination.with_name(destination.name + ".harness-new")
            candidate.write_bytes(rendered)
            conflicts.append(candidate)
            continue

        destination.write_bytes(rendered)

    return conflicts


def run_checked(command: list[str], cwd: Path) -> None:
    """Run a controlled bootstrap command and fail on errors."""
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)  # noqa: S603 -- controlled argv.


def main() -> int:
    """Render the harness and run optional initialization steps."""
    args = parse_args()
    validate_package_name(args.package)
    python_version, ruff_target_version = normalize_python_version(args.python_version)

    template = Path(__file__).resolve().parent / "template"
    target = args.target.resolve()
    values = {
        "project_name": args.name,
        "package_name": args.package,
        "python_version": python_version,
        "ruff_target_version": ruff_target_version,
    }

    if target.exists() and any(target.iterdir()) and not args.merge:
        print(
            f"Target is not empty: {target}. Use --merge to preserve existing files.",
            file=sys.stderr,
        )
        return 2

    target.mkdir(parents=True, exist_ok=True)
    conflicts = copy_template(template, target, values, args.merge)

    hooks_dir = target / ".claude" / "hooks"
    for script in hooks_dir.glob("*.py"):
        script.chmod(script.stat().st_mode | 0o111)

    if args.git_init and not (target / ".git").exists():
        run_checked(["git", "init"], target)

    if args.lock:
        if shutil.which("uv") is None:
            print("uv was not found. Run `uv lock` after installing it.", file=sys.stderr)
        else:
            run_checked(["uv", "lock"], target)

    print(f"Harness rendered in {target}")
    if conflicts:
        print("Review generated conflict files:")
        for conflict in conflicts:
            print(f"  - {conflict.relative_to(target)}")
    print("Next: review AGENTS.md, .claude/settings.json, docs/ARCHITECTURE.md, and docs/MCP.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
