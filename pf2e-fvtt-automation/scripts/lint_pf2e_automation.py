#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

FALLBACK_KEYS = {
    "ActiveEffectLike", "ActorTraits", "AdjustDegreeOfSuccess", "AdjustModifier", "AdjustStrike",
    "Aura", "BaseSpeed", "BattleForm", "ChoiceSet", "CraftingAbility", "CreatureSize",
    "CriticalSpecialization", "DamageAlteration", "DamageDice", "DexterityModifierCap", "EphemeralEffect",
    "FastHealing", "FlatModifier", "GrantItem", "Immunity", "ItemAlteration", "LoseHitPoints",
    "MartialProficiency", "MultipleAttackPenalty", "Note", "Resistance", "RollOption", "RollTwice",
    "Sense", "SpecialResource", "SpecialStatistic", "Strike", "SubstituteRoll", "TempHP",
    "TokenEffectIcon", "TokenImage", "TokenLight", "TokenMark", "TokenName", "Weakness",
}
LEGACY_PATTERNS = [
    (re.compile(r"@Compendium\["), "legacy @Compendium syntax detected; verify and prefer current @UUID syntax"),
]
INVENTED_CONDITION_UUID = re.compile(r"Compendium\.pf2e\.conditionitems\.Item\.([a-z][a-z0-9-]{2,})\b")


def default_root() -> Path:
    value = os.environ.get("PF2E_AUTOMATION_HOME")
    return Path(value).expanduser() if value else Path.home() / ".pf2e-automation"


def load_keys(root: Path) -> set[str]:
    index = root / "sources" / "pf2e" / "src" / "module" / "rules" / "index.ts"
    try:
        text = index.read_text(encoding="utf-8")
    except OSError:
        return set(FALLBACK_KEYS)
    m = re.search(r"static readonly builtin.*?=\s*\{(.*?)\n\s*\};", text, re.DOTALL)
    if not m:
        return set(FALLBACK_KEYS)
    found = set(re.findall(r"^\s*([A-Za-z][A-Za-z0-9]+):\s*", m.group(1), re.MULTILINE))
    return found or set(FALLBACK_KEYS)


def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint PF2e automation JSON/text for common compatibility mistakes.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when warnings are found.")
    args = parser.parse_args()

    path = args.path
    text = path.read_text(encoding="utf-8", errors="replace")
    warnings: list[str] = []
    errors: list[str] = []

    for pattern, message in LEGACY_PATTERNS:
        if pattern.search(text):
            warnings.append(message)

    for match in INVENTED_CONDITION_UUID.finditer(text):
        warnings.append(f"condition UUID ends in slug-like value '{match.group(1)}'; verify the real compendium document ID")

    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON: {exc}")
            data = None
        if data is not None:
            keys = load_keys(args.root.expanduser().resolve())
            for obj in walk(data):
                key = obj.get("key")
                if isinstance(key, str):
                    if key not in keys:
                        warnings.append(f"unknown Rule Element key '{key}' for the current/fallback registry")
                    if key == "AdjustDegreeOfSuccess" and "type" in obj:
                        warnings.append("AdjustDegreeOfSuccess contains historical field 'type'; verify against the installed PF2e schema")
                if key == "GrantItem" and isinstance(obj.get("uuid"), str):
                    if obj["uuid"].endswith(".Item") or obj["uuid"].count(".") < 3:
                        warnings.append("GrantItem uuid looks incomplete; resolve a verified document UUID")

    for token in ("@Check[", "@Damage[", "@Template[", "@UUID["):
        if text.count(token) and text.count(token) > text.count("]"):
            warnings.append(f"possible unterminated inline token: {token}")

    for item in errors:
        print(f"ERROR: {item}")
    for item in sorted(set(warnings)):
        print(f"WARN: {item}")
    if not errors and not warnings:
        print("OK: no common PF2e automation lint issues found")

    if errors:
        return 2
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
