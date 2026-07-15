# Python Engineering Harness plugin

Reusable Claude Code plugin with Python agents, skills, safety hooks, and MCP governance.

Test locally:

```bash
claude --plugin-dir ./plugin/python-engineering-harness
```

Validate:

```bash
claude plugin validate ./plugin/python-engineering-harness
```

The plugin is disabled by default when installed from a marketplace because hooks can block actions,
format changed Python files, and scan the changed worktree before Claude stops. Review the scripts
before enabling.

Project-specific architecture, permissions, and policy remain in each repository.

## MCP behavior

The plugin provides the `mcp-integrator` agent, `/configure-mcp`, `/review-mcp`, and a `PreToolUse`
guard for MCP calls. The guard blocks likely credential exfiltration, escalates state-changing MCP
tools for explicit confirmation, and denies mutations that target production.

The plugin does not bundle a generic MCP server. Put reviewed project integrations in `.mcp.json`
and organization-wide catalogs in managed MCP policy.
