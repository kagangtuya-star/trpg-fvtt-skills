#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


AGENT_COMMANDS = {
    "codex": "codex",
    "claude": "claude",
    "cursor": "cursor",
    "opencode": "opencode",
    "gemini": "gemini",
    "vscode": "code",
    "copilot": "copilot",
}

# Flags documented by the current ctx7 CLI. Gemini is intentionally omitted:
# the CLI can auto-detect universal agents, while a dedicated --gemini flag is not assumed.
TARGET_FLAGS = {
    "codex": "--codex",
    "claude": "--claude",
    "cursor": "--cursor",
    "opencode": "--opencode",
    "vscode": "--vscode",
    "devin": "--devin",
    "copilot": "--copilot",
}


def detect_agents() -> list[str]:
    return [name for name, command in AGENT_COMMANDS.items() if shutil.which(command)]


def context7_already_present(cwd: Path) -> bool:
    home = Path.home()
    files = [
        home / ".codex" / "config.toml",
        home / ".claude.json",
        home / ".cursor" / "mcp.json",
        home / ".opencode.json",
        cwd / ".mcp.json",
        cwd / ".cursor" / "mcp.json",
        cwd / "AGENTS.md",
        cwd / "CLAUDE.md",
    ]
    pattern = re.compile(r"context7|mcp\.context7\.com|@upstash/context7", re.IGNORECASE)
    for path in files:
        try:
            if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                return True
        except OSError:
            pass
    return bool(shutil.which("ctx7"))


def shell_render(cmd: list[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(cmd)
    import shlex
    return shlex.join(cmd)


def setup_command(agent: str, mode: str, scope: str) -> tuple[list[str] | None, str]:
    cmd = ["npx", "ctx7@latest", "setup"]
    note = ""

    if mode == "mcp":
        cmd.append("--mcp")
    elif mode == "cli":
        cmd.append("--cli")

    flag = TARGET_FLAGS.get(agent)
    if flag:
        cmd.append(flag)
    elif agent == "antigravity":
        if mode == "mcp":
            note = "Antigravity has no assumed dedicated MCP flag; use interactive/auto detection or generic MCP configuration."
            return None, note
        cmd.extend(["--cli", "--antigravity"] if "--cli" not in cmd else ["--antigravity"])
    elif agent in {"gemini", "auto", "universal"}:
        note = "No dedicated target flag is assumed; ctx7 setup will use its current auto-detection/universal path."
    elif agent == "generic-mcp":
        note = "Configure the hosted MCP endpoint in the agent's own MCP settings; no client-specific files will be mutated."
        return None, note

    if scope == "project":
        cmd.append("--project")
    return cmd, note


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview or configure Context7 for multiple AI coding agents.")
    parser.add_argument(
        "--agent",
        choices=["auto", "universal", "codex", "claude", "cursor", "opencode", "gemini", "vscode", "devin", "copilot", "antigravity", "generic-mcp"],
        default="auto",
    )
    parser.add_argument("--client", dest="legacy_client", help=argparse.SUPPRESS)
    parser.add_argument("--mode", choices=["auto", "mcp", "cli"], default="auto")
    parser.add_argument("--scope", choices=["global", "project"], default="global")
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="Execute setup. Without this flag, only preview.")
    parser.add_argument("--force", action="store_true", help="Run even when Context7 already appears configured.")
    args = parser.parse_args()

    # Backward compatibility with the first revision of the skill.
    if args.legacy_client and args.agent == "auto":
        args.agent = args.legacy_client if args.legacy_client != "generic" else "generic-mcp"

    cwd = args.cwd.expanduser().resolve()
    detected = detect_agents()
    print("Detected agents: " + (", ".join(detected) if detected else "none in PATH"))

    if context7_already_present(cwd) and not args.force:
        print("Context7 already appears configured or the ctx7 CLI is installed. No mutation planned.")
        print("Use --force only when you intentionally want to rerun Context7 setup.")
        return 0

    agent = args.agent
    if agent == "auto":
        if len(detected) == 1:
            agent = detected[0]
        else:
            agent = "universal"

    cmd, note = setup_command(agent, args.mode, args.scope)
    print(f"Agent target: {agent}")
    print(f"Mode: {args.mode}; scope: {args.scope}")
    if note:
        print(note)

    if cmd is None:
        print("Generic MCP endpoint: https://mcp.context7.com/mcp")
        print("Use the agent's MCP configuration UI/file and an OAuth flow or secret-backed Authorization header as supported by that client.")
        return 0

    print("Planned command:")
    print("  " + shell_render(cmd))
    if not args.apply:
        print("Preview only. Re-run with --apply to execute.")
        return 0

    if not shutil.which("npx"):
        print("npx is required for automatic ctx7 setup. Install Node.js 18+ or configure Context7 as a generic MCP server.", file=sys.stderr)
        return 2

    result = subprocess.run(cmd, check=False, cwd=cwd)
    if result.returncode != 0:
        return result.returncode
    print("Context7 setup completed. Restart or open a new agent session if the client requires it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
