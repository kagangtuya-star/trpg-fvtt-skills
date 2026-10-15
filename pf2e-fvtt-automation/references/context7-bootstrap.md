# Context7 bootstrap

## Portable setup principle

Context7 is a documentation provider, not a dependency on one particular agent. Reuse an already-connected Context7 tool first. Only mutate the workstation when the current environment needs a local CLI, skill, or MCP registration.

Current Context7 provides two main integration modes:

- **MCP**: the agent calls Context7 documentation tools natively.
- **CLI + Skills**: the agent is instructed to query current docs through the `ctx7` CLI without requiring MCP.

The CLI requires Node.js 18+ for the npm/npx path. Installation commands and supported target flags can change, so verify current official Context7 documentation before applying changes when web access is available.

## Preferred CLI

Use the current CLI without a permanent global installation:

```text
npx ctx7@latest setup
```

Useful documented targets include Codex, Claude Code, Cursor, OpenCode, VS Code, Devin, and Copilot; exact target availability can evolve. Use `ctx7 --help` or official docs before relying on a flag. For Gemini CLI and other universal agents, prefer auto-detection unless a dedicated current flag is documented.

Examples:

```text
npx ctx7@latest setup --codex
npx ctx7@latest setup --claude
npx ctx7@latest setup --cursor
npx ctx7@latest setup --opencode
```

The setup flow can choose MCP or CLI+Skills. Project-local setup can be preferable for shared repositories.

## Generic MCP fallback

Context7 supports MCP clients through the hosted endpoint:

```text
https://mcp.context7.com/mcp
```

Configure this through the client's own documented MCP mechanism. Use OAuth when the client supports MCP OAuth, or a secret-backed API key/header mechanism. Do not put an API key into this skill, source control, generated instructions, or a checked-in MCP file.

## Skill scripts

Use `scripts/doctor.py` to detect the current platform, agent CLIs, and traces of existing Context7 setup.

Use `scripts/setup_context7.py --agent auto` to preview setup. It supports explicit common-agent targets and deliberately falls back to Context7 auto-detection or generic MCP instructions for agents whose config format/flag is not known.

Add `--mode mcp` or `--mode cli` only when the desired integration is known. Add `--scope project` for repository-local setup when supported. Add `--apply` only after environment mutation is authorized.

## Behavior rules

- If native Context7 tools are already available, do not reinstall.
- If Context7 is already configured in another surface of the same agent family, prefer reuse.
- Do not assume Codex-style TOML, Claude-style MCP files, or Cursor-style JSON for an unknown agent.
- Do not require Node just to use local PF2e documentation.
- Do not overwrite unrelated MCP configuration or agent instructions.
- After setup, verify an actual library resolution and documentation query rather than checking only that a config file exists.
