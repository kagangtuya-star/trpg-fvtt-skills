#!/usr/bin/env python3
"""Lightweight linter for GLUniverse/PF2e inline automation text."""

from __future__ import annotations

import re
import sys
from pathlib import Path

CONDITIONS = {
    "blinded", "broken", "clumsy", "concealed", "confused", "controlled",
    "dazzled", "deafened", "doomed", "drained", "dying", "encumbered",
    "enfeebled", "fascinated", "fatigued", "fleeing", "frightened",
    "grabbed", "hidden", "immobilized", "invisible", "off-guard",
    "paralyzed", "petrified", "prone", "quickened", "restrained", "sickened",
    "slowed", "stunned", "stupefied", "unconscious", "undetected",
    "unfriendly", "unnoticed", "wounded",
}

DAMAGE_PHRASE = re.compile(
    r"\b\d+d\d+(?:\s*[+-]\s*\d+)?\s+"
    r"(?:acid|bleed|bludgeoning|cold|electricity|fire|force|mental|piercing|poison|precision|slashing|sonic|spirit|vitality|void)\s+damage\b",
    re.IGNORECASE,
)


def iter_directives(text: str, name: str):
    marker = f"@{name}["
    start = 0
    while True:
        pos = text.find(marker, start)
        if pos < 0:
            return
        i = pos + len(marker)
        depth = 1
        while i < len(text) and depth:
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
            i += 1
        if depth:
            yield pos, len(text), text[pos:]
            return
        end = i
        if end < len(text) and text[end] == "{":
            close = text.find("}", end + 1)
            if close >= 0:
                end = close + 1
        yield pos, end, text[pos:end]
        start = end


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: lint_inline.py <text-file>")
        return 2

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    for pos, end, directive in iter_directives(text, "Template"):
        inner = directive.split("[", 1)[1].split("]", 1)[0]
        if "type:" not in inner:
            warnings.append(f"Template at offset {pos} omits canonical 'type:' field: {directive[:100]}")
        if not re.search(r"(?:^|\|)distance:\d+", inner):
            errors.append(f"Template at offset {pos} has no numeric distance: {directive[:100]}")

    for pos, end, directive in iter_directives(text, "Damage"):
        if directive.count("[") != directive.count("]"):
            errors.append(f"Unbalanced @Damage at offset {pos}: {directive[:120]}")
        label_match = re.search(r"\{([^}]*)\}\s*$", directive)
        if label_match and DAMAGE_PHRASE.search(label_match.group(1)):
            errors.append(
                f"@Damage label at offset {pos} contains a plain English damage phrase that the importer may nest: {label_match.group(1)!r}"
            )

    for pos, end, directive in iter_directives(text, "Check"):
        if directive.count("[") != directive.count("]"):
            errors.append(f"Unbalanced @Check at offset {pos}: {directive[:120]}")
        label_match = re.search(r"\{([^}]*)\}\s*$", directive)
        if label_match and re.search(r"\b(?:DC\s+\d+\s+(?:Fortitude|Fort|Reflex|Ref|Will)|(?:Fortitude|Fort|Reflex|Ref|Will)\s+DC\s+\d+)\b", label_match.group(1), re.I):
            errors.append(f"@Check label at offset {pos} contains an importer auto-link phrase: {label_match.group(1)!r}")

    uuid_pattern = re.compile(r"@UUID\[[^\]]+\]\{([^}]*)\}", re.IGNORECASE)
    for match in uuid_pattern.finditer(text):
        label = match.group(1)
        english = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)?", label)
        if any(word.lower() in CONDITIONS for word in english):
            errors.append(
                f"@UUID label at offset {match.start()} contains an English condition slug and may be nested by autoLinkText: {label!r}"
            )

    for line_no, line in enumerate(text.splitlines(), 1):
        has_template = "@Template[" in line
        has_damage = "@Damage[" in line
        has_check = "@Check[" in line
        if has_template and has_damage and "options:area-damage" not in line:
            warnings.append(f"Line {line_no}: area/template damage lacks options:area-damage")
        if has_template and has_check and "options:area-effect" not in line:
            warnings.append(f"Line {line_no}: area/template check lacks options:area-effect")

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARN: {message}")

    if not errors and not warnings:
        print("OK: no inline-automation issues detected")
    elif not errors:
        print(f"OK with {len(warnings)} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
