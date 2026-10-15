---
name: pf2e-fvtt-statblock-author
description: Author, convert, revise, and import Pathfinder 2e NPC, monster, boss, hazard, Strike, spellcasting, inventory, effect/aura, and creature-ability data for Foundry VTT PF2e. Use whenever the user provides or requests a Chinese or English PF2e/PF2SBC-style creature card and wants an FVTT-ready complete Actor, asks for full-stat synchronization, or needs individual abilities with clickable @Check/@Damage/@Template automation. Prefer the bundled unified Actor JSON workflow for complete creatures, compact ability JSON for isolated abilities, and GLUniverse strict Markdown only when explicitly requested. Never guess compendium UUIDs.
---

# PF2e FVTT Statblock Author

## Core workflow

1. Read `references/importer-inline-syntax.md` before writing any FVTT-ready mechanic.
2. For a complete Chinese/English creature or hazard card, read `references/complete-actor-import.md` and emit the complete Actor JSON accepted by `assets/fvtt-pf2e-unified-importer.js`.
3. For only one or several abilities, read `references/macro-item-import.md`; emit compact ability JSON. The unified macro accepts this payload too.
4. Use GLUniverse strict Markdown only when the user explicitly asks for GLUniverse/importer Markdown or needs that interchange format.
5. Keep player-facing prose in the user's language. Keep PF2e slugs, damage types, check types, Rule Element keys, frequency values, and command keywords in canonical English.
6. Convert textual rolls, saves, damage, and measured areas into explicit PF2e inline syntax. Do not rely on a second auto-link pass when exact automation matters.
7. Never invent compendium UUIDs. Let the live PF2e system resolve conditions; use spell/item UUIDs only when supplied or verified.
8. Validate the exact final payload before returning it.

## Output routing

### Complete Actor JSON — default for full monsters/hazards

Use when the input contains a complete stat block or the user wants Foundry to create/synchronize the whole Actor.

- Read `references/complete-actor-import.md`.
- Emit `{ "schema": "pf2e-fvtt-actor", "version": 1, "actor": ... }`.
- Populate all explicit core fields: level, rarity, size, creature traits, perception/senses, languages, skills, six ability modifiers, AC, saves, HP, speed, I/W/R, notes, and hazard fields where relevant.
- Populate `attacks`, `actions`, `spellcasting`, `inventory`, and `effects` as structured arrays.
- Preserve unusual mechanics in descriptions/notes rather than discarding them.
- Item granularity (user convention): when modes are **discrete selectable alternatives** ("choose one of the following N omens/phases"), emit **one Item per mode**, plus a short core/overview Item holding the shared trigger, frequency, and global modifiers. Never collapse a mode menu into one Item.
  - Each split Item must be self-sufficient: repeat the trigger, the shared-frequency note, and any global modifier (e.g. an anchor/weakening rule) in every mode's `description`, because a GM may open a single Item mid-session.
  - Put the shared `frequency` only on the core Item; mode Items omit it so they are not tracked as separate cooldowns.
  - Also emit an `all-<name>.json` bundle (all items in one `items` array) so the set can be imported in one paste.
  - Only merge modes into a single `description` with `【Section Name】` headings when they are one inseparable mechanic (one action that always does A then B).
- Save the exact JSON and run `python scripts/validate_actor_payload.py <payload.json>` before returning it.
- When the user asks for the macro, provide `assets/fvtt-pf2e-unified-importer.js`.

### Ability JSON — preferred for isolated abilities

Use for one ability, several abilities, boss phases, reactions, passive abilities, telegraphed attacks, or mechanics meant to become owned Action Items without synchronizing an entire Actor.

- Read `references/macro-item-import.md`.
- Emit a JSON array or `{ "items": [...] }` accepted by the unified macro.
- Apply the item-granularity rule above: split discrete selectable modes into separate Items; keep one `description` per Item rather than splitting into separate Markdown headings.
- Run `python scripts/validate_actor_payload.py <payload.json>`.

### GLUniverse strict Markdown — compatibility mode

Use only when the user explicitly asks for GLUniverse strict Markdown or wants to use the module UI/parser directly.

- Follow `references/importer-inline-syntax.md`.
- Avoid importer second-pass nesting hazards.
- For long multi-mode abilities prefer JSON unless strict Markdown was explicitly requested.

## Inline conventions

Use these forms by default:

- `@Check[fortitude|dc:32]`
- `@Check[reflex|dc:32|basic|options:area-effect]`
- `@Check[will|dc:32|options:area-effect,damaging-effect]`
- `@Check[athletics|dc:32]`
- `@Check[flat|dc:5]`
- `@Damage[6d6[void]]`
- `@Damage[6d6[void]|options:area-damage]`
- `@Damage[5d6[cold],3d6[void]|options:area-damage]`
- `@Template[type:burst|distance:20]`
- `@Template[type:cone|distance:30]`
- `@Template[type:line|distance:60|width:10]`
- `[[/gmr 1d20+22 #Counteract Ability]]{反制 +22}`

`basic` already supplies the damaging-effect roll option. Add `options:area-damage` for area damage and `options:area-effect` for checks caused by an area.

## Conditions

Use plain bilingual condition text and let the live PF2e `ConditionManager` resolve it:

```text
失败：获得迟缓 Slowed 1，持续1轮。
```

Never fabricate `Compendium.pf2e.conditionitems.Item.<slug>` IDs.

## Validation

For complete Actor or ability JSON:

1. Save the exact final JSON to a temporary UTF-8 file.
2. Run `python scripts/validate_actor_payload.py <file>`.
3. Fix all `ERROR` findings and review `WARN` findings.
4. Return the same validated JSON.

For strict Markdown without JSON, run `python scripts/lint_inline.py <file>` instead.

## Bundled Foundry macros

`assets/fvtt-pf2e-unified-importer.js` is the preferred macro. It:

- creates a complete NPC/Hazard from the Skill JSON;
- synchronizes core Actor fields to an existing NPC/Hazard;
- fully rebuilds only Items previously managed by this macro, preserving hand-made Items;
- imports Strikes, Action/Reaction/Free/Passive abilities, spellcasting entries, matched spells, inventory, Effects/Auras, and verified Rule Elements;
- preserves unmatched spell names in the spellcasting description instead of silently losing them;
- resolves capitalized English PF2e condition names through the live ConditionManager;
- normalizes literal `\\n` and real newlines into Foundry HTML line breaks/headings;
- accepts compact ability payloads and optional GLUniverse strict Markdown fallback.

`assets/fvtt-pf2e-ability-item-importer.js` is retained only for backward compatibility with older ability-only workflows.

## Source of truth

Treat the installed PF2e system as authoritative for runtime enums, condition UUIDs, document schemas, and compendium content. Treat the GLUniverse importer architecture as the reference model for Actor/item separation and strict Markdown compatibility. Use `references/complete-actor-import.md` for the direct complete-Actor JSON contract, `references/macro-item-import.md` for ability-only details, and `references/importer-inline-syntax.md` for inline syntax/importer hazards.
