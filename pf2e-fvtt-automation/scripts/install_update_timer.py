#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

TAG = "# pf2e-fvtt-automation-update"
TASK_NAME = "PF2eAutomationSourceRefresh"
LAUNCHD_LABEL = "com.pf2e.automation.source-refresh"


def default_root() -> Path:
    value = os.environ.get("PF2E_AUTOMATION_HOME")
    return Path(value).expanduser() if value else Path.home() / ".pf2e-automation"


def systemd_available() -> bool:
    if not shutil.which("systemctl"):
        return False
    try:
        p = subprocess.run(["systemctl", "--user", "show-environment"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return p.returncode == 0
    except Exception:
        return False


def auto_mode() -> str:
    system = platform.system()
    if system == "Windows" and shutil.which("schtasks"):
        return "windows"
    if system == "Darwin" and shutil.which("launchctl"):
        return "launchd"
    if system == "Linux":
        if systemd_available():
            return "systemd"
        if shutil.which("crontab"):
            return "cron"
    return "none"


def sync_command(root: Path) -> list[str]:
    script = Path(__file__).resolve().with_name("sync_sources.py")
    python = Path(sys.executable).resolve()
    return [str(python), str(script), "--root", str(root), "--force", "--refresh-configured"]


def quote_systemd(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def install_systemd(root: Path, apply: bool, hour: int, minute: int) -> None:
    user_dir = Path.home() / ".config" / "systemd" / "user"
    service = user_dir / "pf2e-automation-update.service"
    timer = user_dir / "pf2e-automation-update.timer"
    cmd = sync_command(root)
    exec_start = " ".join(quote_systemd(part) for part in cmd)
    service_text = "\n".join([
        "[Unit]",
        "Description=Refresh PF2e automation documentation and configured source mirrors",
        "",
        "[Service]",
        "Type=oneshot",
        f"ExecStart={exec_start}",
        "",
    ])
    timer_text = "\n".join([
        "[Unit]",
        "Description=Weekly PF2e automation source refresh",
        "",
        "[Timer]",
        f"OnCalendar=Sun *-*-* {hour:02d}:{minute:02d}:00",
        "Persistent=true",
        "",
        "[Install]",
        "WantedBy=timers.target",
        "",
    ])
    print(f"Would write {service} and {timer} and enable the timer.")
    if not apply:
        return
    user_dir.mkdir(parents=True, exist_ok=True)
    service.write_text(service_text, encoding="utf-8")
    timer.write_text(timer_text, encoding="utf-8")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", timer.name], check=True)


def install_cron(root: Path, apply: bool, hour: int, minute: int) -> None:
    if not shutil.which("crontab"):
        raise RuntimeError("crontab is not available")
    cmd = sync_command(root)
    import shlex
    line = f"{minute} {hour} * * 0 {shlex.join(cmd)} {TAG}"
    existing = subprocess.run(["crontab", "-l"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
    kept = [x for x in existing.splitlines() if TAG not in x]
    new_text = "\n".join(kept + [line]) + "\n"
    print("Would install cron entry:")
    print(line)
    if not apply:
        return
    subprocess.run(["crontab", "-"], input=new_text, text=True, check=True)


def install_windows(root: Path, apply: bool, hour: int, minute: int) -> None:
    if not shutil.which("schtasks"):
        raise RuntimeError("schtasks is not available")
    action = subprocess.list2cmdline(sync_command(root))
    time_text = f"{hour:02d}:{minute:02d}"
    cmd = [
        "schtasks", "/Create", "/F", "/TN", TASK_NAME,
        "/SC", "WEEKLY", "/D", "SUN", "/ST", time_text,
        "/TR", action,
    ]
    print("Would create Windows Task Scheduler task:")
    print(subprocess.list2cmdline(cmd))
    if not apply:
        return
    subprocess.run(cmd, check=True)


def install_launchd(root: Path, apply: bool, hour: int, minute: int) -> None:
    if not shutil.which("launchctl"):
        raise RuntimeError("launchctl is not available")
    launch_dir = Path.home() / "Library" / "LaunchAgents"
    plist_path = launch_dir / f"{LAUNCHD_LABEL}.plist"
    payload = {
        "Label": LAUNCHD_LABEL,
        "ProgramArguments": sync_command(root),
        "StartCalendarInterval": {"Weekday": 0, "Hour": hour, "Minute": minute},
        "RunAtLoad": False,
        "StandardOutPath": str(root / "source-refresh.log"),
        "StandardErrorPath": str(root / "source-refresh.err.log"),
    }
    print(f"Would write and load {plist_path}")
    if not apply:
        return
    launch_dir.mkdir(parents=True, exist_ok=True)
    root.mkdir(parents=True, exist_ok=True)
    with plist_path.open("wb") as fh:
        plistlib.dump(payload, fh)
    subprocess.run(["launchctl", "unload", str(plist_path)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install an optional weekly updater across Windows, macOS, Linux, and WSL-capable environments.")
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--mode", choices=["auto", "systemd", "cron", "windows", "launchd", "none"], default="auto")
    parser.add_argument("--hour", type=int, default=4)
    parser.add_argument("--minute", type=int, default=17)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not (0 <= args.hour <= 23 and 0 <= args.minute <= 59):
        print("Invalid hour/minute.", file=sys.stderr)
        return 2

    root = args.root.expanduser().resolve()
    mode = auto_mode() if args.mode == "auto" else args.mode
    print(f"Scheduler mode: {mode}")

    if mode == "none":
        print("No supported background scheduler was found. The skill's freshness gate still updates sources when used.")
        return 0
    try:
        if mode == "systemd":
            install_systemd(root, args.apply, args.hour, args.minute)
        elif mode == "cron":
            install_cron(root, args.apply, args.hour, args.minute)
        elif mode == "windows":
            install_windows(root, args.apply, args.hour, args.minute)
        elif mode == "launchd":
            install_launchd(root, args.apply, args.hour, args.minute)
    except Exception as exc:
        print(f"Could not install {mode} updater: {exc}", file=sys.stderr)
        print("Use the freshness gate instead: sync_sources.py --ensure-fresh --max-age-days 7 --refresh-configured")
        return 2

    if not args.apply:
        print("Preview only. Re-run with --apply to install.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
