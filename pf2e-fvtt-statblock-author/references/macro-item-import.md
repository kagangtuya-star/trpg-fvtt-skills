# FVTT PF2e Ability Item Import Macro

## Purpose

Use `assets/fvtt-pf2e-unified-importer.js` for new workflows. It accepts the same compact ability payloads in addition to complete Actor payloads. `assets/fvtt-pf2e-ability-item-importer.js` remains available only for backward compatibility when the user specifically wants the older ability-only macro.

The ability-payload mode intentionally has a narrower scope than complete Actor synchronization:

- Import/update Action, Reaction, Free Action, and Passive ability items.
- Preserve explicit PF2e inline syntax in descriptions and let the installed PF2e system enrich it at render time.
- Resolve capitalized English PF2e condition names such as `Frightened`, `Slowed`, and `Drained` against the live `game.pf2e.ConditionManager` and create verified `@UUID` links at import time.
- Use the selected NPC/Hazard token as the default target, but allow choosing another NPC/Hazard Actor.
- Update an existing Action item with the same name by default instead of duplicating it.
- Accept strict Markdown as a convenience when `gluniverse-pf2e-statsblock-import` is active, using that module's exposed `api.parse()` parser.

Use the unified macro complete Actor payload for entire NPC/Hazard actors, spellcasting entries, inventory, effects/auras, and core statistics. Use GLUniverse strict Markdown only when explicitly requested.

## Preferred JSON payload

For one or more abilities, emit a JSON object like this:

```json
{
  "version": 1,
  "items": [
    {
      "name": "熵之尖啸 Entropic Shriek",
      "actionType": "action",
      "actions": 2,
      "category": "offensive",
      "traits": ["auditory", "divine", "void"],
      "frequency": "1 per round",
      "description": "对@Template[type:cone|distance:30]范围内所有生物造成@Damage[10d6[sonic]|options:area-damage]伤害（@Check[will|dc:29|basic|options:area-effect,inflicts:frightened]豁免）。豁免失败获得惊惧 Frightened 1；大失败获得惊惧 Frightened 2。"
    }
  ]
}
```

Supported fields:

- `name`: required.
- `actionType`: `action`, `reaction`, `free`, or `passive`.
- `actions`: 1-3; only used for `action`.
- `category`: normally `offensive`, `defensive`, or `interaction`.
- `traits`: array of PF2e trait slugs.
- `frequency`: either a string such as `1 per round` / `1 per day`, or `{ "max": 1, "value": 1, "per": "round" }`.
- `description`: raw ability text containing explicit PF2e inline directives.
- `rules`: optional raw PF2e Rule Element array. Only emit rules when the user supplied them or their correctness can be verified.
- `img`: optional item image path.

## Why JSON is preferred for ability items

JSON avoids ambiguity between Markdown structure and long multi-mode ability descriptions. In particular, a telegraphed boss ability can contain many named modes in one `description` without accidentally creating separate `###` blocks.

Do not emit full PF2e Item source JSON. Emit the compact logical payload above and let the macro construct the current Action Item shape.

## Description rules in macro mode

The macro does not run the GLUniverse importer's `autoLinkText()` over descriptions. Therefore:

- Always author `@Check`, `@Damage`, and `@Template` explicitly.
- `[[/gmr ...]]` is preserved verbatim.
- Plain capitalized English condition names are intentionally allowed, e.g. `惊惧 Frightened 1`; the macro resolves them against the live PF2e ConditionManager.
- Never invent condition compendium UUIDs.
- `inflicts:<slug>` is still only a roll option; it does not itself apply the condition.

## Strict Markdown convenience mode

When the GLUniverse importer module is active, the macro also accepts action blocks such as:

```markdown
## Actions

### 熵之尖啸 Entropic Shriek
Type: action
Actions: 2
Category: offensive
Traits: auditory, divine, void
Frequency: 1 per round
Description: 对@Template[type:cone|distance:30]范围内所有生物造成@Damage[10d6[sonic]|options:area-damage]伤害（@Check[will|dc:29|basic|options:area-effect,inflicts:frightened]豁免）。失败获得惊惧 Frightened 1。
```

For long or multi-mode descriptions, prefer JSON rather than forcing the content into importer Markdown.

When the modes are discrete selectable alternatives ("choose one of the following N omens/phases"), emit one Item per mode in that JSON instead of one Item with all modes in a single `description`. Make each mode Item self-sufficient (repeat the trigger, the shared-frequency note, and any global modifier inside it), keep the shared `frequency` only on a separate core/overview Item, and additionally emit an `all-<name>.json` bundle containing every Item for a one-paste import.

## Delivery workflow

When the user asks for an FVTT-ready individual monster ability:

1. Author and balance the mechanic.
2. Write all inline checks/damage/templates explicitly according to `importer-inline-syntax.md`.
3. Package the ability in the preferred JSON payload.
4. Run `scripts/lint_inline.py` against the final payload text.
5. Return the JSON as the ready-to-import data.
6. If the user asks for the macro itself, return `assets/fvtt-pf2e-unified-importer.js` unless they explicitly request the legacy ability-only macro.
