# Python Engineering Harness plugin

Reusable Claude Code plugin with Python engineering agents, skills, safety hooks, MCP governance, and an engineering output style.

Test locally:

```bash
claude --plugin-dir ./plugin/python-engineering-harness
```

Validate:

```bash
claude plugin validate ./plugin/python-engineering-harness
```

The plugin is disabled by default when installed from a marketplace because hooks can block actions and format changed Python files. Review the scripts before enabling.

Project-specific architecture, permissions, and policy still belong in each repository's `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, and `.claude/settings.json`.

## MCP behavior

The plugin provides the `mcp-integrator` agent, `/configure-mcp`, `/review-mcp`, and a `PreToolUse` guard for MCP calls. The guard blocks likely credential exfiltration and escalates state-changing MCP tools for explicit confirmation.

The plugin intentionally does not bundle a generic MCP server. Project integrations belong in a reviewed `.mcp.json`, while organization-wide catalogs belong in managed MCP policy. This avoids adding external trust and data-egress paths to every repository by default.
