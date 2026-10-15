# Environment and agent portability

## Purpose

Keep PF2e automation knowledge and tooling usable across operating systems and AI agents. Do not couple the workflow to one shell, one home-directory layout, or one agent's MCP format.

## Capability-first model

Classify the current environment by capability before choosing a setup path:

1. **Connected documentation tool exists**: use the agent's native Context7 connector/tool directly. No local installation is required.
2. **Shell + `ctx7`/`npx` exists**: use Context7 CLI or its official setup command.
3. **MCP-capable agent without official CLI target**: use the hosted Context7 MCP endpoint and the client's documented MCP configuration mechanism. Do not guess a config schema.
4. **Persistent shell but no Context7**: local Git mirrors still provide the PF2e Rule Element guide and optional source tree; web/GitHub can fill gaps.
5. **Ephemeral/read-only agent**: skip persistent installation and background scheduling. Query current remote sources on demand and state that no local mirror was retained.

Local knowledge mirrors are a cache, not a prerequisite for correctness.

## Operating-system matrix

| Environment | Local mirror | Optional scheduler | Notes |
| --- | --- | --- | --- |
| Windows | Python + Git | Task Scheduler | Use native paths; do not require WSL. |
| WSL | Python + Git | systemd-user or cron when enabled | Do not assume WSL stays running; always keep the freshness gate. |
| Linux desktop/server | Python + Git | systemd-user, then cron | Headless OAuth/device flows may still work; avoid GUI assumptions. |
| macOS | Python + Git | launchd | Keep generated files under the user's home unless a project-local root is requested. |
| Container/CI/cloud agent | only if filesystem is writable/persistent | usually none | Prefer project-local cache; otherwise query remote sources per run. |

`scripts/doctor.py` reports the current platform, WSL state, candidate schedulers, agent CLIs, Context7 traces, and local mirror state.

## Agent matrix

The skill should work with at least these agent families without changing its PF2e authoring behavior:

- **Codex**: Context7 can be configured by `ctx7 setup --codex`; Codex CLI/Desktop/IDE surfaces may share configuration. Prefer existing connected tools when already present.
- **Claude Code**: use the current Context7 `--claude` setup path or the agent's MCP configuration. Project-local setup is useful in repositories shared by a team.
- **Cursor**: use the current `--cursor` setup path when desired; otherwise reuse existing MCP configuration.
- **OpenCode**: use the current `--opencode` path.
- **VS Code / Copilot / Devin**: the Context7 CLI currently exposes setup targets for supported clients; verify `ctx7 --help` or current docs before mutation because flags may evolve.
- **Gemini CLI**: treat it as a universal/auto-detected agent unless current Context7 documentation exposes a dedicated flag. Never invent `--gemini`.
- **Antigravity and other skill-directory agents**: use the current Context7 CLI skill-install path if documented; otherwise use the universal `.agents/skills` convention only when the client documents support for it.
- **Unknown MCP clients**: use `https://mcp.context7.com/mcp` through that client's own MCP configuration. Do not write guessed config files.
- **ChatGPT or another agent with a native Context7 connector**: call the connector directly and skip workstation installation entirely.

## Context7 install policy

Prefer the current official `npx ctx7@latest setup` flow. It can choose MCP or CLI+Skills modes and supports auto-detection. Use explicit client flags only when they are documented for the current CLI.

Node.js 18+ is required for the npm/npx route, but Node is not required merely to read the local Git mirror. If Node is missing, do not install it automatically unless the user asks; use native Context7 tools, a generic MCP configuration, or remote documentation instead.

Never persist an API key in the skill or repository. Use OAuth, device flow, environment variables, OS secret stores, or the agent's secret mechanism.

## Knowledge-root policy

Default root:

```text
~/.pf2e-automation/
```

Override with `PF2E_AUTOMATION_HOME` or `--root`. Prefer a project-local root such as `.pf2e-automation/` when the execution environment is ephemeral but the repository itself persists.

The manifest records configured source URLs, PF2e ref, whether packs are mirrored, commit SHA, and last successful sync. Scheduled refreshes use `--refresh-configured` so they do not silently revert a custom mirror or source profile.

## Safe mutation rules

- Preview setup and scheduler changes before applying them.
- Do not overwrite unrelated MCP servers or agent instructions.
- Do not install package-manager dependencies automatically.
- Do not create global configuration when the user requested a project-local setup.
- Treat agent config formats as versioned external APIs. If a format is uncertain, consult current documentation instead of guessing.
- A failed background scheduler is not fatal: the per-use freshness gate remains the correctness fallback.
