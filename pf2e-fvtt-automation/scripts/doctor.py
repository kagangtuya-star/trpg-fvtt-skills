#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path


def default_root() -> Path:
    value = os.environ.get("PF2E_AUTOMATION_HOME")
    return Path(value).expanduser() if value else Path.home() / ".pf2e-automation"


def command_version(cmd: list[str]) -> str | None:
    try:
        p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=8, check=False)
        return p.stdout.strip().splitlines()[0] if p.stdout.strip() else None
    except Exception:
        return None


def is_wsl() -> bool:
    if platform.system() != "Linux":
        return False
    if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
        return True
    try:
        text = Path("/proc/version").read_text(encoding="utf-8", errors="ignore")
        return "microsoft" in text.lower()
    except OSError:
        return False


def platform_info() -> dict:
    system = platform.system()
    scheduler = []
    if system == "Windows" and shutil.which("schtasks"):
        scheduler.append("windows-task-scheduler")
    if system == "Darwin" and shutil.which("launchctl"):
        scheduler.append("launchd")
    if system == "Linux":
        if shutil.which("systemctl"):
            scheduler.append("systemd-user")
        if shutil.which("crontab"):
            scheduler.append("cron")
    return {
        "system": system,
        "release": platform.release(),
        "machine": platform.machine(),
        "wsl": is_wsl(),
        "shell": os.environ.get("SHELL") or os.environ.get("ComSpec"),
        "scheduler_candidates": scheduler,
    }


AGENT_COMMANDS: dict[str, list[str]] = {
    "codex": ["codex", "--version"],
    "claude-code": ["claude", "--version"],
    "gemini-cli": ["gemini", "--version"],
    "cursor": ["cursor", "--version"],
    "opencode": ["opencode", "--version"],
    "vscode": ["code", "--version"],
    "copilot-cli": ["copilot", "--version"],
}


def detect_agents() -> dict[str, dict[str, str | None]]:
    report: dict[str, dict[str, str | None]] = {}
    for agent, cmd in AGENT_COMMANDS.items():
        exe = cmd[0]
        path = shutil.which(exe)
        report[agent] = {"path": path, "version": command_version(cmd) if path else None}
    return report


def context7_candidate_paths(cwd: Path) -> list[Path]:
    home = Path.home()
    return [
        home / ".codex" / "config.toml",
        home / ".claude.json",
        home / ".claude" / "settings.json",
        home / ".cursor" / "mcp.json",
        home / ".opencode.json",
        home / ".config" / "opencode" / "opencode.json",
        home / ".config" / "opencode" / "opencode.jsonc",
        cwd / ".mcp.json",
        cwd / ".cursor" / "mcp.json",
        cwd / ".opencode.json",
        cwd / ".vscode" / "mcp.json",
        cwd / "AGENTS.md",
        cwd / "CLAUDE.md",
    ]


def context7_skill_dirs(cwd: Path) -> list[Path]:
    home = Path.home()
    rels = [
        ".agents/skills",
        ".claude/skills",
        ".cursor/skills",
        ".devin/skills",
        ".agent/skills",
    ]
    return [home / rel for rel in rels] + [cwd / rel for rel in rels]


def find_context7(cwd: Path) -> dict:
    pattern = re.compile(r"context7|mcp\.context7\.com|@upstash/context7", re.IGNORECASE)
    config_hits = []
    for path in context7_candidate_paths(cwd):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if pattern.search(text):
            config_hits.append(str(path))

    skill_hits = []
    for root in context7_skill_dirs(cwd):
        if not root.exists():
            continue
        try:
            for child in root.iterdir():
                if "context7" in child.name.lower() or child.name.lower() in {"find-docs", "context7-cli"}:
                    skill_hits.append(str(child))
        except OSError:
            pass

    return {
        "ctx7_cli": shutil.which("ctx7"),
        "config_hits": sorted(set(config_hits)),
        "skill_hits": sorted(set(skill_hits)),
        "configured": bool(config_hits or skill_hits),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a PF2e automation workstation across common OS and agent environments.")
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--cwd", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    cwd = args.cwd.expanduser().resolve()
    base_tools = {}
    for name, version_cmd in {
        "git": ["git", "--version"],
        "python": [os.fspath(Path(os.sys.executable)), "--version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "npx": ["npx", "--version"],
    }.items():
        exe = version_cmd[0]
        exists = Path(exe).exists() if os.path.isabs(exe) else bool(shutil.which(exe))
        base_tools[name] = {
            "path": exe if os.path.isabs(exe) and exists else shutil.which(exe),
            "version": command_version(version_cmd) if exists else None,
        }

    docs = root / "sources" / "foundry-pf2e-wiki-doc"
    pf2e = root / "sources" / "pf2e"
    manifest = root / "manifest.json"
    agents = detect_agents()
    context7 = find_context7(cwd)
    report = {
        "root": str(root),
        "cwd": str(cwd),
        "platform": platform_info(),
        "tools": base_tools,
        "agents": agents,
        "context7": context7,
        "docs_mirror": {"exists": docs.exists(), "path": str(docs)},
        "pf2e_source_mirror": {"exists": pf2e.exists(), "path": str(pf2e)},
        "manifest": {"exists": manifest.exists(), "path": str(manifest)},
    }

    node_ok = False
    node_version = base_tools["node"]["version"] or ""
    m = re.search(r"v?(\d+)", node_version)
    if m:
        node_ok = int(m.group(1)) >= 18
    report["node_18_plus"] = node_ok

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        p = report["platform"]
        wsl_note = " (WSL)" if p["wsl"] else ""
        print(f"Platform: {p['system']} {p['release']} {p['machine']}{wsl_note}")
        print(f"PF2e automation root: {root}")
        for name, info in base_tools.items():
            print(f"{name:10s}: {info['version'] or 'missing'}")
        print(f"Node >=18: {'yes' if node_ok else 'no'}")
        detected_agents = [name for name, info in agents.items() if info["path"]]
        print("Agents: " + (", ".join(detected_agents) if detected_agents else "none detected in PATH"))
        print(f"Context7: {'configured/detected' if context7['configured'] or context7['ctx7_cli'] else 'not detected'}")
        if context7["config_hits"]:
            print("Context7 config: " + ", ".join(context7["config_hits"]))
        print("Schedulers: " + (", ".join(p["scheduler_candidates"]) if p["scheduler_candidates"] else "none detected"))
        print(f"Rule Element docs: {'ready' if docs.exists() else 'missing'}")
        print(f"PF2e source mirror: {'ready' if pf2e.exists() else 'optional/not present'}")

    required_ok = bool(base_tools["git"]["path"]) and docs.exists()
    if args.strict and not required_ok:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
