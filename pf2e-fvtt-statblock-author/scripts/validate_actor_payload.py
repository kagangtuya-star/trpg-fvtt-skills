#!/usr/bin/env python3
"""Validate compact PF2e FVTT actor/ability JSON emitted by the skill."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = "pf2e-fvtt-actor"
MAX_VERSION = 1
ABILITY_KEYS = {"str", "dex", "con", "int", "wis", "cha"}
ACTION_TYPES = {"action", "reaction", "free", "passive"}
ACTOR_KINDS = {"npc", "hazard"}
RARITIES = {"common", "uncommon", "rare", "unique"}
SIZES = {"tiny", "sm", "med", "lg", "huge", "grg"}
DAMAGE_TYPES = {
    "acid", "bleed", "bludgeoning", "cold", "electricity", "fire", "force",
    "mental", "piercing", "poison", "slashing", "sonic", "spirit", "vitality", "void",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def is_num(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def iter_text(value: Any):
    if isinstance(value, dict):
        for k, v in value.items():
            if k in {"description", "details", "disable", "routine", "reset"} and isinstance(v, str):
                yield v
            else:
                yield from iter_text(v)
    elif isinstance(value, list):
        for v in value:
            yield from iter_text(v)


def validate_actor(actor: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if not str(actor.get("name", "")).strip():
        fail(errors, "actor.name is required")
    if actor.get("kind", "npc") not in ACTOR_KINDS:
        fail(errors, f"actor.kind must be one of {sorted(ACTOR_KINDS)}")
    if not isinstance(actor.get("level"), int):
        fail(errors, "actor.level must be an integer")
    if actor.get("rarity", "common") not in RARITIES:
        fail(errors, f"actor.rarity must be one of {sorted(RARITIES)}")
    if actor.get("size", "med") not in SIZES:
        fail(errors, f"actor.size must be one of {sorted(SIZES)}")

    abilities = actor.get("abilities", {})
    missing = ABILITY_KEYS.difference(abilities.keys())
    if missing:
        fail(errors, f"actor.abilities missing: {', '.join(sorted(missing))}")

    for key in ("ac", "hp"):
        value = actor.get(key)
        if not isinstance(value, dict) or not is_num(value.get("value")):
            fail(errors, f"actor.{key}.value must be numeric")

    saves = actor.get("saves", {})
    for key in ("fortitude", "reflex", "will"):
        value = saves.get(key)
        if not (is_num(value) or (isinstance(value, dict) and is_num(value.get("value")))):
            fail(errors, f"actor.saves.{key} must be numeric or {{value, details}}")

    for i, attack in enumerate(actor.get("attacks", [])):
        if not str(attack.get("name", "")).strip():
            fail(errors, f"actor.attacks[{i}].name is required")
        if attack.get("type", "melee") not in {"melee", "ranged"}:
            fail(errors, f"actor.attacks[{i}].type must be melee or ranged")
        if not is_num(attack.get("bonus", 0)):
            fail(errors, f"actor.attacks[{i}].bonus must be numeric")
        rolls = attack.get("damageRolls", [])
        if not isinstance(rolls, (list, dict)):
            fail(errors, f"actor.attacks[{i}].damageRolls must be a list or object")
        if isinstance(rolls, list):
            for j, roll in enumerate(rolls):
                if not str(roll.get("formula", "")).strip():
                    fail(errors, f"actor.attacks[{i}].damageRolls[{j}].formula is required")
                dtype = roll.get("type")
                if dtype and dtype not in DAMAGE_TYPES:
                    warnings.append(f"unknown damage type {dtype!r} on attack {attack.get('name')!r}; live PF2e may reject it")

    for i, action in enumerate(actor.get("actions", [])):
        if not str(action.get("name", "")).strip():
            fail(errors, f"actor.actions[{i}].name is required")
        atype = action.get("actionType", "action")
        if atype not in ACTION_TYPES:
            fail(errors, f"actor.actions[{i}].actionType must be one of {sorted(ACTION_TYPES)}")
        if atype == "action" and action.get("actions") not in {1, 2, 3}:
            fail(errors, f"actor.actions[{i}].actions must be 1, 2, or 3")

    for i, entry in enumerate(actor.get("spellcasting", [])):
        if not str(entry.get("name", "")).strip():
            fail(errors, f"actor.spellcasting[{i}].name is required")
        if entry.get("tradition", "arcane") not in {"arcane", "divine", "occult", "primal"}:
            fail(errors, f"actor.spellcasting[{i}].tradition is invalid")
        if entry.get("prepared", "innate") not in {"prepared", "spontaneous", "innate", "focus", "ritual"}:
            fail(errors, f"actor.spellcasting[{i}].prepared is invalid")
        for j, spell in enumerate(entry.get("spells", [])):
            if isinstance(spell, dict) and not str(spell.get("name", "")).strip():
                fail(errors, f"actor.spellcasting[{i}].spells[{j}].name is required")

    for key in ("inventory", "effects", "notes"):
        if key in actor and not isinstance(actor[key], list):
            fail(errors, f"actor.{key} must be a list")


def validate_abilities(items: list[Any], errors: list[str]) -> None:
    for i, action in enumerate(items):
        if not isinstance(action, dict):
            fail(errors, f"items[{i}] must be an object")
            continue
        if not str(action.get("name", "")).strip():
            fail(errors, f"items[{i}].name is required")
        atype = action.get("actionType", action.get("type", "action"))
        if atype not in ACTION_TYPES:
            fail(errors, f"items[{i}].actionType must be one of {sorted(ACTION_TYPES)}")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_actor_payload.py <payload.json>")
        return 2

    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid JSON: {exc}")
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    if isinstance(payload, list):
        validate_abilities(payload, errors)
        root = payload
    elif isinstance(payload, dict) and isinstance(payload.get("items"), list) and "actor" not in payload:
        validate_abilities(payload["items"], errors)
        root = payload
    elif isinstance(payload, dict):
        version = payload.get("version", 1)
        if not isinstance(version, int) or version > MAX_VERSION:
            fail(errors, f"version must be an integer <= {MAX_VERSION}")
        schema = payload.get("schema", SCHEMA)
        if schema != SCHEMA:
            fail(errors, f"schema must be {SCHEMA!r}")
        actor = payload.get("actor")
        if not isinstance(actor, dict):
            fail(errors, "actor object is required")
        else:
            validate_actor(actor, errors, warnings)
        root = payload
    else:
        fail(errors, "root must be an object or ability array")
        root = payload

    # Reuse the inline linter over all user-facing description text.
    texts = list(iter_text(root))
    if texts:
        lint_script = Path(__file__).with_name("lint_inline.py")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as fh:
            fh.write("\n\n".join(texts))
            temp_path = fh.name
        proc = subprocess.run([sys.executable, str(lint_script), temp_path], capture_output=True, text=True)
        Path(temp_path).unlink(missing_ok=True)
        for line in proc.stdout.splitlines():
            if line.startswith("ERROR:"):
                errors.append(f"inline: {line[6:].strip()}")
            elif line.startswith("WARN:"):
                warnings.append(f"inline: {line[5:].strip()}")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")
    if not errors:
        print(f"OK: payload valid ({len(warnings)} warning(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
