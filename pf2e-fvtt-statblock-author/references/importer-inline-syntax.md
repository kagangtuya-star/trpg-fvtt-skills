# GLUniverse PF2e Importer Inline Syntax Reference

## Contents

1. Source and processing pipeline
2. Inline checks
3. Inline damage
4. Templates
5. Conditions and UUIDs
6. GM rolls
7. Importer-specific hazards
8. Ready-to-use patterns

## 1. Source and processing pipeline

Analyzed source:
`https://raw.githubusercontent.com/kagangtuya-star/gluniverse-pf2e-statsblock-import/refs/heads/main/scripts/importer.js`

The importer stores ability descriptions as text, then `htmlDescription()` performs roughly this pipeline:

1. HTML-escape the source description.
2. Preserve line breaks with `<br>`.
3. Pass the escaped text through `autoLinkText()`.
4. Store the resulting HTML in the PF2e item description.

Important `autoLinkText()` behavior from the importer:

- `DC 32 Fortitude` or `Fortitude DC 32` becomes an inline `@Check[type:fortitude|dc:32|showDC:all]`.
- English damage text such as `6d6 void damage` becomes an inline `@Damage[(6d6)[void]]{6d6 void damage}`.
- English PF2e condition names are replaced with a `@UUID[...]` condition link resolved from the live PF2e ConditionManager when possible.
- Existing `@Check`, `@Damage`, `@Template`, and Foundry inline-roll syntax are otherwise ordinary text during this pass and remain available for PF2e enrichment later.

The importer obtains live damage types from `CONFIG.PF2E.damageTypes`, live condition slugs from the PF2e ConditionManager / config, and rule-element keys from the installed system when available. Prefer valid current PF2e slugs.

## 2. Inline checks

Preferred current PF2e form omits `type:` because the first parameter is understood as the check type:

```text
@Check[fortitude|dc:32|basic]
@Check[reflex|dc:32|basic|options:area-effect]
@Check[will|dc:29|basic|options:area-effect,inflicts:frightened]
@Check[flat|dc:5]
@Check[athletics|dc:32]
@Check[arcana,occultism|dc:32]
```

The importer's own auto-link output uses the also-valid explicit form:

```text
@Check[type:fortitude|dc:32|showDC:all]
```

For generated explicit data blocks, prefer the shorter canonical PF2e form unless matching an existing source exactly.

### Basic vs non-basic damaging saves

A basic save automatically carries PF2e's `damaging-effect` roll option:

```text
@Check[reflex|dc:32|basic|options:area-effect]
```

For a damaging save that is not basic, add it explicitly:

```text
@Check[fortitude|dc:32|options:area-effect,damaging-effect]
```

### Roll options

Common options for monster abilities:

- `area-effect` — the check comes from an area effect.
- `damaging-effect` — the non-basic check comes from a damaging effect.
- `inflicts:frightened` — exposes that the effect can inflict frightened to downstream automation.
- Other `inflicts:<slug>` values may be used when the condition slug is valid.

`inflicts:` does not by itself apply a condition to a token.

## 3. Inline damage

Basic forms:

```text
@Damage[10d6[sonic]]
@Damage[(2d6+4)[slashing]]
@Damage[5d6[cold],3d6[void]]
```

Area damage:

```text
@Damage[10d6[sonic]|options:area-damage]
@Damage[5d6[cold],3d6[void]|options:area-damage]
```

Persistent damage:

```text
@Damage[1d6[persistent,fire]]
```

Avoid unnecessary custom labels. In this importer, a label containing a plain parseable damage phrase can be scanned by `autoLinkText()` again. Prefer:

```text
@Damage[10d6[sonic]|options:area-damage]伤害
```

instead of:

```text
@Damage[10d6[sonic]|options:area-damage]{10d6 sonic damage}
```

when the text is going through the GLUniverse importer.

## 4. Templates

Author measured-template links explicitly. The importer does not synthesize them from Chinese prose.

Canonical forms:

```text
@Template[type:emanation|distance:40]
@Template[type:burst|distance:20]
@Template[type:cone|distance:30]
@Template[type:line|distance:60]
@Template[type:line|distance:60|width:10]
```

Use `width` for a line wider than the default 5 feet, and for square/rectangular regions represented as wide lines.

A custom label is possible, but usually unnecessary:

```text
@Template[type:line|distance:120|width:10]{120×10尺线形}
```

## 5. Conditions and UUIDs

The importer recognizes English PF2e condition slugs such as `Frightened`, `Slowed`, `Drained`, `Enfeebled`, `Clumsy`, `Prone`, `Immobilized`, `Stupefied`, and `Off-Guard` and resolves them against the live PF2e condition manager.

Recommended importer-targeted Chinese text:

```text
豁免失败的生物获得惊惧 Frightened 1；大失败获得惊惧 Frightened 2。
```

Do not invent a condition UUID from its slug. Real PF2e compendium document IDs are not guaranteed to equal the condition slug.

### Existing @UUID pitfall

The importer's condition auto-link guard only looks shortly before a matched condition word. An explicit long `@UUID[...]` whose custom label also contains the English condition name can therefore be vulnerable to a nested replacement.

If an exact UUID is already known and must be emitted for importer input, prefer a label without the English slug:

```text
@UUID[Compendium.pf2e.conditionitems.Item.ACTUAL_ID]{惊惧 1}
```

Otherwise use plain `惊惧 Frightened 1` and let the importer resolve the condition link.

## 6. GM rolls

Use Foundry inline rolls for non-damage numeric rolls. Monster cooldowns normally use GM-only rolls:

```text
[[/gmr 1d4 #Recharge Shrieking Scream]]{1d4轮}
```

Counteract modifier example:

```text
[[/gmr 1d20+22 #Counteract Omen of Unmaking]]{反制 +22}
```

Use `@Damage` rather than generic `[[/r ...]]` for actual damage so PF2e damage automation can interact with the roll.

## 7. Importer-specific hazards

### Nested damage links

Unsafe for this importer:

```text
@Damage[10d6[sonic]]{10d6 sonic damage}
```

The label itself matches the importer's plain-English damage regex and can be transformed again.

Safe:

```text
@Damage[10d6[sonic]]伤害
```

### Nested condition links

Avoid:

```text
@UUID[...]{惊惧 Frightened 1}
```

when that text will be passed through this importer's `autoLinkText()`.

Prefer plain:

```text
惊惧 Frightened 1
```

or a verified UUID with a Chinese-only label.

### Nested check links

Avoid placing plain auto-link forms such as `DC 32 Fortitude` inside an `@Check` custom label. Keep the label short or omit it.

### HTML

The importer HTML-escapes description source. Do not rely on custom raw HTML in descriptions. Use PF2e enrich syntax and Markdown/plain text instead.

## 8. Ready-to-use patterns

### Area damage + basic save + condition

```text
对@Template[type:cone|distance:30]范围内的所有生物造成@Damage[10d6[sonic]|options:area-damage]伤害（@Check[will|dc:29|basic|options:area-effect,inflicts:frightened]豁免）。豁免失败的生物获得惊惧 Frightened 1（大失败获得惊惧 Frightened 2）。
```

### Area damage + non-basic save

```text
对@Template[type:burst|distance:20]范围内所有生物造成@Damage[6d6[void]|options:area-damage]伤害，并要求其进行@Check[fortitude|dc:32|options:area-effect,damaging-effect,inflicts:drained]豁免。
```

### Wide line

```text
鬼祟之暗在60尺内指定一道@Template[type:line|distance:60|width:10]区域。熵灾爆发时，对区域内所有生物造成@Damage[5d6[cold],3d6[void]|options:area-damage]伤害（@Check[reflex|dc:32|basic|options:area-effect,inflicts:slowed]豁免）。
```

### Recharge

```text
此后该生物在[[/gmr 1d4 #Recharge Ability Name]]{1d4轮}内不能再次使用此能力。
```
