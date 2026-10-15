#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

EXTENSIONS = {".md", ".json", ".ts", ".js", ".mjs", ".cjs"}
SKIP_PARTS = {".git", "node_modules", "uploads", "dist", "build"}


def default_root() -> Path:
    value = os.environ.get("PF2E_AUTOMATION_HOME")
    return Path(value).expanduser() if value else Path.home() / ".pf2e-automation"


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Search local PF2e automation docs/source for examples.")
    parser.add_argument("query", nargs="+", help="Case-insensitive terms or regex patterns.")
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--regex", action="store_true")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--context", type=int, default=1, help="Context lines around each match.")
    args = parser.parse_args()

    base = args.root.expanduser().resolve() / "sources"
    if not base.exists():
        print(f"No local sources found at {base}. Run sync_sources.py first.")
        return 2

    patterns = []
    for term in args.query:
        patterns.append(re.compile(term if args.regex else re.escape(term), re.IGNORECASE))

    count = 0
    for path in iter_files(base):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines):
            if not all(p.search(line) for p in patterns):
                continue
            start = max(0, idx - args.context)
            end = min(len(lines), idx + args.context + 1)
            print(f"\n{path}:{idx + 1}")
            for n in range(start, end):
                marker = ">" if n == idx else " "
                print(f"{marker} {n + 1:5d}: {lines[n]}")
            count += 1
            if count >= args.limit:
                return 0
    if count == 0:
        print("No matches.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
