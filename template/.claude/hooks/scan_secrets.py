#!/usr/bin/env python3
"""Detect high-confidence secrets in files just written by Claude Code."""

import re
from pathlib import Path
from typing import Any

from _common import block_action, log_event, path_within, project_root, read_input

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI API key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)


def file_path(tool_input: Any) -> str | None:
    """Extract a file path from an Edit or Write tool payload."""
    if not isinstance(tool_input, dict):
        return None
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return None


def main() -> None:
    """Block continuation when a high-confidence secret appears in a changed file."""
    payload = read_input()
    root = project_root(payload)
    raw = file_path(payload.get("tool_input"))
    if raw is None:
        return

    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    if not path_within(path, root) or not path.is_file() or path.stat().st_size > 2_000_000:
        return
    if path.name.endswith(".example") or ".example." in path.name:
        return

    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return

    findings = [name for name, pattern in PATTERNS if pattern.search(content)]
    if findings:
        log_event(payload, "scan_secrets", "secret-in-file", "block")
        block_action(
            f"Potential secret detected in {path.relative_to(root)}: "
            f"{', '.join(findings)}. Remove it and rotate it if real. "
            "Use a secret manager or environment-variable placeholder."
        )


if __name__ == "__main__":
    main()
