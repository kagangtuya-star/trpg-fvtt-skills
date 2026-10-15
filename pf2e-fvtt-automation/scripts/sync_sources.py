#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DOCS_URL = "https://github.com/kagangtuya-star/foundry-pf2e-wiki-doc.git"
PF2E_URL = "https://github.com/foundryvtt/pf2e.git"
DEFAULT_PF2E_REF = "v14-dev"
DOC_SPARSE = [
    "AGENTS.md",
    "docs/*.md",
    "docs/Going-Deeper-Topics/*.md",
    "docs/Getting-Started-Guide/*.md",
]
PF2E_SPARSE = [
    "src/module/rules",
    "src/module/system",
    "src/module/actor",
    "src/module/item",
    "src/module/chat-message",
]


def default_root() -> Path:
    value = os.environ.get("PF2E_AUTOMATION_HOME")
    return Path(value).expanduser() if value else Path.home() / ".pf2e-automation"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git(*args: str, cwd: Path | None = None) -> str:
    cmd = ["git"]
    if cwd:
        cmd += ["-C", str(cwd)]
    cmd += list(args)
    result = run(cmd, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git command failed ({result.returncode}): {' '.join(cmd)}\n{detail}")
    return result.stdout.strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"sources": {}}


def save_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def is_fresh(entry: dict, max_age_days: float) -> bool:
    stamp = entry.get("synced_at_epoch")
    if not isinstance(stamp, (int, float)):
        return False
    return (time.time() - stamp) <= max_age_days * 86400


def clone_docs(dest: Path, url: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    git("clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(dest))
    git("sparse-checkout", "set", "--no-cone", *DOC_SPARSE, cwd=dest)


def update_docs(dest: Path) -> None:
    git("fetch", "--depth", "1", "origin", "main", cwd=dest)
    git("reset", "--hard", "origin/main", cwd=dest)
    git("sparse-checkout", "set", "--no-cone", *DOC_SPARSE, cwd=dest)


def clone_pf2e(dest: Path, ref: str, with_packs: bool, url: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    git("clone", "--depth", "1", "--branch", ref, "--filter=blob:none", "--sparse", url, str(dest))
    sparse = list(PF2E_SPARSE)
    if with_packs:
        sparse.append("packs/pf2e")
    git("sparse-checkout", "set", *sparse, cwd=dest)


def update_pf2e(dest: Path, ref: str, with_packs: bool) -> None:
    git("fetch", "--depth", "1", "origin", ref, cwd=dest)
    git("checkout", "-B", ref, f"origin/{ref}", cwd=dest)
    sparse = list(PF2E_SPARSE)
    if with_packs:
        sparse.append("packs/pf2e")
    git("sparse-checkout", "set", *sparse, cwd=dest)


def sync_repo(name: str, dest: Path, manifest: dict, max_age_days: float, force: bool, updater, cloner) -> None:
    entry = manifest.setdefault("sources", {}).setdefault(name, {})
    if not force and dest.exists() and is_fresh(entry, max_age_days):
        print(f"{name}: fresh; skipped ({dest})")
        return

    try:
        if (dest / ".git").exists():
            updater(dest)
        else:
            if dest.exists():
                backup = dest.with_name(dest.name + ".stale")
                if backup.exists():
                    shutil.rmtree(backup)
                dest.replace(backup)
            cloner(dest)
        sha = git("rev-parse", "HEAD", cwd=dest)
        entry.update({
            "path": str(dest),
            "commit": sha,
            "synced_at": now_iso(),
            "synced_at_epoch": time.time(),
        })
        entry.pop("last_error", None)
        entry.pop("last_attempt_at", None)
        print(f"{name}: {sha[:12]} ({dest})")
    except Exception as exc:
        entry["last_error"] = str(exc)
        entry["last_attempt_at"] = now_iso()
        print(f"{name}: sync failed: {exc}", file=sys.stderr)
        if not dest.exists():
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync PF2e automation documentation and optional source mirror.")
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--max-age-days", type=float, default=7.0)
    parser.add_argument("--ensure-fresh", action="store_true", help="Skip network work when the mirror is still fresh.")
    parser.add_argument("--force", action="store_true", help="Force a fetch/update now.")
    parser.add_argument("--with-pf2e-source", action="store_true", help="Maintain a sparse foundryvtt/pf2e source mirror.")
    parser.add_argument("--with-packs", action="store_true", help="Include packs/pf2e in the sparse PF2e source mirror.")
    parser.add_argument("--refresh-configured", action="store_true", help="Refresh optional sources using the profile already recorded in manifest.json.")
    parser.add_argument("--pf2e-ref", default=None)
    parser.add_argument("--docs-url", default=None, help="Override the Rule Element documentation Git URL.")
    parser.add_argument("--pf2e-url", default=None, help="Override the PF2e system Git URL.")
    args = parser.parse_args()

    if not shutil.which("git"):
        print("git is required to sync sources.", file=sys.stderr)
        return 2

    root = args.root.expanduser().resolve()
    sources = root / "sources"
    manifest_path = root / "manifest.json"
    manifest = load_manifest(manifest_path)

    configured = manifest.get("sources", {})
    docs_entry = configured.get("foundry-pf2e-wiki-doc", {})
    pf2e_entry = configured.get("foundryvtt-pf2e", {})
    docs_url = args.docs_url or (docs_entry.get("url") if args.refresh_configured else None) or DOCS_URL
    pf2e_url = args.pf2e_url or (pf2e_entry.get("url") if args.refresh_configured else None) or PF2E_URL
    pf2e_ref = args.pf2e_ref or (pf2e_entry.get("ref") if args.refresh_configured else None) or DEFAULT_PF2E_REF
    with_pf2e_source = args.with_pf2e_source or (args.refresh_configured and bool(pf2e_entry))
    with_packs = args.with_packs or (args.refresh_configured and bool(pf2e_entry.get("with_packs")))

    effective_force = args.force or not args.ensure_fresh
    sync_repo(
        "foundry-pf2e-wiki-doc",
        sources / "foundry-pf2e-wiki-doc",
        manifest,
        args.max_age_days,
        effective_force,
        update_docs,
        lambda dest: clone_docs(dest, docs_url),
    )
    manifest["sources"]["foundry-pf2e-wiki-doc"]["url"] = docs_url

    if with_pf2e_source:
        sync_repo(
            "foundryvtt-pf2e",
            sources / "pf2e",
            manifest,
            args.max_age_days,
            effective_force,
            lambda dest: update_pf2e(dest, pf2e_ref, with_packs),
            lambda dest: clone_pf2e(dest, pf2e_ref, with_packs, pf2e_url),
        )
        manifest["sources"]["foundryvtt-pf2e"]["ref"] = pf2e_ref
        manifest["sources"]["foundryvtt-pf2e"]["with_packs"] = bool(with_packs)
        manifest["sources"]["foundryvtt-pf2e"]["url"] = pf2e_url

    manifest["updated_at"] = now_iso()
    save_manifest(manifest_path, manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
